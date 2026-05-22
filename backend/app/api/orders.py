from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.order import OrderDetail, OrderSummary
from app.services.demo_data import get_demo_order_detail, get_demo_order_summaries
from app.services.order_status import get_customer_orders, get_order_detail

router = APIRouter(prefix="/orders", tags=["orders"])


def _is_demo_mode() -> bool:
    return not settings.MYOB_BASE_URL


@router.get("", response_model=list[OrderSummary])
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if _is_demo_mode():
        return get_demo_order_summaries()
    if not current_user.myob_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No MYOB customer ID linked to your account. Contact admin.",
        )
    return await get_customer_orders(current_user.myob_customer_id, db)


@router.get("/{order_nbr}", response_model=OrderDetail)
async def get_order(
    order_nbr: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if _is_demo_mode():
        order = get_demo_order_detail(order_nbr)
        if order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        return order
    if not current_user.myob_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No MYOB customer ID linked to your account. Contact admin.",
        )
    order = await get_order_detail(order_nbr, current_user.myob_customer_id, db)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order
