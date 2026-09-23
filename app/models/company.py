from __future__ import annotations

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_companies_singleton"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(160), nullable=False)
    trade_name: Mapped[str] = mapped_column(
        String(160),
        nullable=False,
        default="",
        server_default="",
    )
    tax_id: Mapped[str] = mapped_column(String(11), nullable=False)
    tax_condition: Mapped[str] = mapped_column(String(50), nullable=False)
    fiscal_address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    province: Mapped[str] = mapped_column(String(120), nullable=False)
    postal_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="",
        server_default="",
    )
    phone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="",
        server_default="",
    )
    email: Mapped[str] = mapped_column(
        String(254),
        nullable=False,
        default="",
        server_default="",
    )
