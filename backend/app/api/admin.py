from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_admin_user
from app.core.security import get_password_hash
from app.database import get_db
from app.models.inspection import InspectionRecord
from app.models.user import User
from app.schemas.order import InspectionRequest
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
def list_users(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    return db.query(User).order_by(User.id).all()


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    req: UserCreate,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        company_name=req.company_name,
        myob_customer_id=req.myob_customer_id,
        is_admin=req.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    req: UserUpdate,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updates = req.model_dump(exclude_unset=True)
    if user_id == current_admin.id and updates.get("is_active") is False:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    for field, value in updates.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


@router.post("/inspect", status_code=status.HTTP_201_CREATED)
def mark_inspected(
    req: InspectionRequest,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(InspectionRecord)
        .filter_by(sales_order_nbr=req.sales_order_nbr, line_nbr=req.line_nbr)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Line already marked as inspected",
        )
    record = InspectionRecord(
        sales_order_nbr=req.sales_order_nbr,
        line_nbr=req.line_nbr,
        inspected_by=admin.email,
        notes=req.notes,
    )
    db.add(record)
    db.commit()
    return {"message": "Line marked as inspected"}


@router.delete("/inspect/{sales_order_nbr}/{line_nbr}", status_code=status.HTTP_204_NO_CONTENT)
def unmark_inspected(
    sales_order_nbr: str,
    line_nbr: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(InspectionRecord)
        .filter_by(sales_order_nbr=sales_order_nbr, line_nbr=line_nbr)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="Inspection record not found")
    db.delete(record)
    db.commit()
