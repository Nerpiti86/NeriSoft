"""add company and company permission

Revision ID: 0004_company
Revises: 0003_roles_permissions
Create Date: 2026-09-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_company"
down_revision: Union[str, None] = "0003_roles_permissions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


COMPANY_PERMISSION = {
    "code": "system.company.manage",
    "module": "Empresa",
    "name": "Administrar datos de empresa",
    "description": "Consultar y actualizar los datos generales y fiscales de la empresa.",
}


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("legal_name", sa.String(length=160), nullable=False),
        sa.Column("trade_name", sa.String(length=160), server_default="", nullable=False),
        sa.Column("tax_id", sa.String(length=11), nullable=False),
        sa.Column("tax_condition", sa.String(length=50), nullable=False),
        sa.Column("fiscal_address", sa.String(length=255), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("province", sa.String(length=120), nullable=False),
        sa.Column("postal_code", sa.String(length=20), server_default="", nullable=False),
        sa.Column("phone", sa.String(length=50), server_default="", nullable=False),
        sa.Column("email", sa.String(length=254), server_default="", nullable=False),
        sa.CheckConstraint("id = 1", name="ck_companies_singleton"),
        sa.PrimaryKeyConstraint("id"),
    )

    permissions_table = sa.table(
        "permissions",
        sa.column("code", sa.String),
        sa.column("module", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    op.bulk_insert(permissions_table, [COMPANY_PERMISSION])


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM permissions WHERE code = :code").bindparams(
            code=COMPANY_PERMISSION["code"]
        )
    )
    op.drop_table("companies")
