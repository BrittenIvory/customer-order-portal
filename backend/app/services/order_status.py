"""Order status calculation logic.

Determines the status of each sales order line based on:
1. Waiting for Production - PO exists, requested date > 3 weeks away
2. In Production - PO requested date within 3 weeks
3. In Transit to Warehouse - PO requested date is blank/removed
4. In Our Warehouse - PO line has been received
5. Inspected & Ready to Ship - Manually marked in portal
6. Shipped to Customer - SO line has been invoiced
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.inspection import InspectionRecord
from app.schemas.order import (
    OrderDetail,
    OrderLineItem,
    OrderStatus,
    OrderSummary,
    STATUS_ORDER,
)
from app.services.myob import myob_client

logger = logging.getLogger(__name__)

THREE_WEEKS = timedelta(weeks=3)


def _val(field: dict[str, Any] | Any) -> Any:
    """Extract value from MYOB Advanced field format {"value": ...}."""
    if isinstance(field, dict) and "value" in field:
        return field["value"]
    return field


def _parse_date(val: Any) -> datetime | None:
    if val is None:
        return None
    s = _val(val)
    if not s:
        return None
    if isinstance(s, datetime):
        return s
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _determine_line_status(
    po_line: dict[str, Any] | None,
    is_received: bool,
    is_inspected: bool,
    is_invoiced: bool,
) -> OrderStatus:
    if is_invoiced:
        return OrderStatus.SHIPPED
    if is_inspected:
        return OrderStatus.INSPECTED
    if is_received:
        return OrderStatus.IN_WAREHOUSE
    if po_line is None:
        return OrderStatus.WAITING_FOR_PRODUCTION

    requested_date = _parse_date(po_line.get("RequestedDate"))
    if requested_date is None:
        return OrderStatus.IN_TRANSIT

    now = datetime.now(timezone.utc)
    time_until = requested_date - now
    if time_until > THREE_WEEKS:
        return OrderStatus.WAITING_FOR_PRODUCTION
    return OrderStatus.IN_PRODUCTION


def _overall_status(statuses: list[OrderStatus]) -> OrderStatus:
    """The overall order status is the earliest stage among all lines."""
    if not statuses:
        return OrderStatus.WAITING_FOR_PRODUCTION
    earliest_index = min(STATUS_ORDER.index(s) for s in statuses)
    return STATUS_ORDER[earliest_index]


async def _fetch_po_cached(
    po_nbr: str, cache: dict[str, dict[str, Any] | None]
) -> dict[str, Any] | None:
    if po_nbr in cache:
        return cache[po_nbr]
    try:
        po = await myob_client.get_purchase_order(po_nbr)
    except Exception:
        logger.warning("Failed to fetch PO %s", po_nbr)
        po = None
    cache[po_nbr] = po
    return po


def _resolve_po_line(
    po: dict[str, Any] | None, inventory_id: str
) -> tuple[dict[str, Any] | None, bool]:
    if po is None:
        return None, False
    for po_det in po.get("Details", []):
        if _val(po_det.get("InventoryID")) == inventory_id:
            received_qty = _val(po_det.get("ReceivedQty", 0))
            order_qty = _val(po_det.get("OrderQty", 0))
            is_received = bool(
                received_qty and order_qty and received_qty >= order_qty
            )
            return po_det, is_received
    return None, False


async def get_customer_orders(
    customer_id: str, db: Session
) -> list[OrderSummary]:
    try:
        sales_orders = await myob_client.get_sales_orders(customer_id)
    except Exception:
        logger.exception("Failed to fetch sales orders from MYOB")
        return []

    po_cache: dict[str, dict[str, Any] | None] = {}
    summaries: list[OrderSummary] = []

    for so in sales_orders:
        order_nbr = _val(so.get("OrderNbr", ""))
        details = so.get("Details", [])

        line_statuses: list[OrderStatus] = []
        for line in details:
            line_nbr = _val(line.get("LineNbr", 0))
            inventory_id = _val(line.get("InventoryID", ""))
            is_invoiced = _val(line.get("Invoiced", False)) or _val(so.get("Status", "")) == "Invoiced"
            is_inspected = _is_line_inspected(db, order_nbr, line_nbr)

            po_order_nbr = _val(line.get("POOrderNbr"))
            po_line = None
            is_received = False
            if po_order_nbr:
                po = await _fetch_po_cached(po_order_nbr, po_cache)
                po_line, is_received = _resolve_po_line(po, inventory_id)

            status = _determine_line_status(
                po_line, is_received, is_inspected, is_invoiced
            )
            line_statuses.append(status)

        summaries.append(
            OrderSummary(
                order_nbr=order_nbr,
                order_date=_parse_date(so.get("Date")),
                customer_id=_val(so.get("CustomerID", "")),
                customer_name=_val(so.get("CustomerName")),
                description=_val(so.get("Description")),
                overall_status=_overall_status(line_statuses),
                total_amount=_val(so.get("OrderTotal")),
                line_count=len(details),
                estimated_delivery=None,
            )
        )

    return summaries


async def get_order_detail(
    order_nbr: str, customer_id: str, db: Session
) -> OrderDetail | None:
    try:
        so = await myob_client.get_sales_order(order_nbr)
    except Exception:
        logger.exception("Failed to fetch sales order %s from MYOB", order_nbr)
        return None

    if so is None:
        return None

    if _val(so.get("CustomerID", "")) != customer_id:
        return None

    details = so.get("Details", [])
    lines: list[OrderLineItem] = []
    po_cache: dict[str, dict[str, Any] | None] = {}

    for line in details:
        line_nbr = _val(line.get("LineNbr", 0))
        inventory_id = _val(line.get("InventoryID", ""))
        description = _val(line.get("LineDescription"))
        quantity = _val(line.get("OrderQty", 0))
        unit_price = _val(line.get("UnitPrice"))
        line_total = _val(line.get("ExtendedPrice"))

        is_invoiced = _val(line.get("Invoiced", False)) or _val(
            so.get("Status", "")
        ) == "Invoiced"

        is_inspected = _is_line_inspected(db, order_nbr, line_nbr)

        po_order_nbr = _val(line.get("POOrderNbr"))
        po_line = None
        po_requested_date = None
        is_received = False

        if po_order_nbr:
            po = await _fetch_po_cached(po_order_nbr, po_cache)
            po_line, is_received = _resolve_po_line(po, inventory_id)
            if po_line:
                po_requested_date = _parse_date(
                    po_line.get("RequestedDate")
                )

        status = _determine_line_status(
            po_line, is_received, is_inspected, is_invoiced
        )

        lines.append(
            OrderLineItem(
                line_nbr=line_nbr,
                inventory_id=inventory_id,
                description=description,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
                status=status,
                estimated_delivery=po_requested_date,
                po_order_nbr=po_order_nbr,
                po_requested_date=po_requested_date,
                received_date=None,
                inspected_at=_get_inspection_date(db, order_nbr, line_nbr),
                invoiced_at=None,
            )
        )

    overall = _overall_status([l.status for l in lines])

    return OrderDetail(
        order_nbr=order_nbr,
        order_date=_parse_date(so.get("Date")),
        customer_id=_val(so.get("CustomerID", "")),
        customer_name=_val(so.get("CustomerName")),
        customer_order_ref=_val(so.get("CustomerOrder")),
        description=_val(so.get("Description")),
        overall_status=overall,
        total_amount=_val(so.get("OrderTotal")),
        estimated_delivery=None,
        lines=lines,
    )


def _is_line_inspected(db: Session, order_nbr: str, line_nbr: int) -> bool:
    return (
        db.query(InspectionRecord)
        .filter_by(sales_order_nbr=order_nbr, line_nbr=line_nbr)
        .first()
        is not None
    )


def _get_inspection_date(
    db: Session, order_nbr: str, line_nbr: int
) -> datetime | None:
    record = (
        db.query(InspectionRecord)
        .filter_by(sales_order_nbr=order_nbr, line_nbr=line_nbr)
        .first()
    )
    return record.inspected_at if record else None
