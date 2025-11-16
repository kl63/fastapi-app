"""make_order_addresses_optional

Revision ID: 6ff09a43503e
Revises: drop_payment_tables
Create Date: 2025-11-16 09:57:42.794509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6ff09a43503e'
down_revision = 'drop_payment_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make delivery_address_id and billing_address_id nullable
    op.alter_column('order', 'delivery_address_id',
                    existing_type=sa.String(),
                    nullable=True)
    op.alter_column('order', 'billing_address_id',
                    existing_type=sa.String(),
                    nullable=True)


def downgrade() -> None:
    # Revert to non-nullable (be careful - this will fail if NULL values exist)
    op.alter_column('order', 'delivery_address_id',
                    existing_type=sa.String(),
                    nullable=False)
    op.alter_column('order', 'billing_address_id',
                    existing_type=sa.String(),
                    nullable=False)
