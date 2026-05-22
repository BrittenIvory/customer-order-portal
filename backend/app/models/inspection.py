from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, func

from app.database import Base


class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    __table_args__ = (
        UniqueConstraint("sales_order_nbr", "line_nbr", name="uq_inspection_so_line"),
    )

    id = Column(Integer, primary_key=True, index=True)
    sales_order_nbr = Column(String(50), nullable=False, index=True)
    line_nbr = Column(Integer, nullable=False)
    inspected_by = Column(String(255), nullable=True)
    inspected_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
