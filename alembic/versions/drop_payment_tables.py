"""Drop payment tables

Revision ID: drop_payment_tables
Revises: 6235c6122bf8
Create Date: 2025-11-15 06:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'drop_payment_tables'
down_revision = '6235c6122bf8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop payment table first (has foreign key to paymentmethod)
    op.drop_index(op.f('ix_payment_id'), table_name='payment')
    op.drop_table('payment')
    
    # Drop paymentmethod table
    op.drop_index(op.f('ix_paymentmethod_id'), table_name='paymentmethod')
    op.drop_table('paymentmethod')


def downgrade() -> None:
    # Recreate paymentmethod table
    op.create_table('paymentmethod',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=True),
        sa.Column('last_four_digits', sa.String(), nullable=True),
        sa.Column('expiry_month', sa.String(), nullable=True),
        sa.Column('expiry_year', sa.String(), nullable=True),
        sa.Column('cardholder_name', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('payment_metadata', sa.JSON(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_paymentmethod_id'), 'paymentmethod', ['id'], unique=False)
    
    # Recreate payment table
    op.create_table('payment',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('order_id', sa.String(), nullable=False),
        sa.Column('payment_method_id', sa.String(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('transaction_id', sa.String(), nullable=True),
        sa.Column('processor', sa.String(), nullable=True),
        sa.Column('processor_response', sa.JSON(), nullable=True),
        sa.Column('failure_reason', sa.String(), nullable=True),
        sa.Column('failure_code', sa.String(), nullable=True),
        sa.Column('refunded_amount', sa.Float(), nullable=True),
        sa.Column('refund_reason', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
        sa.ForeignKeyConstraint(['payment_method_id'], ['paymentmethod.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payment_id'), 'payment', ['id'], unique=False)
