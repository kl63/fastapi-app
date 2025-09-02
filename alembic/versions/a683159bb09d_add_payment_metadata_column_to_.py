"""Add payment_metadata column to PaymentMethod

Revision ID: a683159bb09d
Revises: 986ffec0cb37
Create Date: 2025-09-02 08:55:19.559797

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a683159bb09d'
down_revision = '31694f4cf0f0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('paymentmethod', sa.Column('payment_metadata', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('paymentmethod', 'payment_metadata')
