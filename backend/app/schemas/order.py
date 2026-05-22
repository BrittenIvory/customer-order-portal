from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class OrderStatus(str, Enum):
    WAITING_FOR_PRODUCTION = "Waiting for Production"
    IN_PRODUCTION = "In Production"
    IN_TRANSIT = "In Transit to Warehouse"
    IN_WAREHOUSE = "In Our Warehouse"
    INSPECTED = "Inspected & Ready to Ship"
    SHIPPED = "Shipped to Customer"


STATUS_ORDER = [
    OrderStatus.WAITING_FOR_PRODUCTION,
    OrderStatus.IN_PRODUCTION,
    OrderStatus.IN_TRANSIT,
    OrderStatus.IN_WAREHOUSE,
    OrderStatus.INSPECTED,
    OrderStatus.SHIPPED,
]


class OrderLineItem(BaseModel):
    line_nbr: int
    inventory_id: str
    description: str | None = None
    quantity: float
    unit_price: float | None = None
    line_total: float | None = None
    status: OrderStatus
    estimated_delivery: datetime | None = None
    po_order_nbr: str | None = None
    po_requested_date: datetime | None = None
    received_date: datetime | None = None
    inspected_at: datetime | None = None
    invoiced_at: datetime | None = None


class OrderSummary(BaseModel):
    order_nbr: str
    order_date: datetime | None = None
    customer_id: str
    customer_name: str | None = None
    description: str | None = None
    overall_status: OrderStatus
    total_amount: float | None = None
    line_count: int
    estimated_delivery: datetime | None = None


class OrderDetail(BaseModel):
    order_nbr: str
    order_date: datetime | None = None
    customer_id: str
    customer_name: str | None = None
    customer_order_ref: str | None = None
    description: str | None = None
    overall_status: OrderStatus
    total_amount: float | None = None
    estimated_delivery: datetime | None = None
    lines: list[OrderLineItem]


class InspectionRequest(BaseModel):
    sales_order_nbr: str
    line_nbr: int
    notes: str | None = None
