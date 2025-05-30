"""updated payments table

Revision ID: f108d6437f59
Revises: 14f4e3448d7b
Create Date: 2025-05-27 12:24:44.452242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'f108d6437f59'
down_revision: Union[str, None] = '14f4e3448d7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    
    # op.add_column('payments', sa.Column('merchant_request_id', sa.String(length=100), nullable=True))
    # op.add_column('payments', sa.Column('phone_number', sa.String(length=50), nullable=False))
    # op.add_column('payments', sa.Column('transaction_id', sa.String(length=100), nullable=True))
    # op.add_column('payments', sa.Column('result_code', sa.Integer(), nullable=True))
    # op.add_column('payments', sa.Column('result_desc', sa.Text(), nullable=True))
    # op.alter_column('payments', 'order_id',
    #            existing_type=mysql.INTEGER(),
    #            nullable=True)
    # op.alter_column('payments', 'status',
    #            existing_type=mysql.VARCHAR(length=50),
    #            type_=sa.String(length=100),
    #            existing_nullable=True)
    # op.drop_index('order_id', table_name='payments')
    # op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    # op.create_index(op.f('ix_payments_order_id'), 'payments', ['order_id'], unique=False)
    # op.create_unique_constraint(None, 'payments', ['checkout_request_id'])
    # op.drop_constraint('payments_ibfk_1', 'payments', type_='foreignkey')
    # op.drop_column('payments', 'paid_at')
    # op.drop_column('payments', 'mpesa_receipt')
    # # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('payments', sa.Column('mpesa_receipt', mysql.VARCHAR(length=100), nullable=True))
    op.add_column('payments', sa.Column('paid_at', mysql.DATETIME(), nullable=True))
    op.create_foreign_key('payments_ibfk_1', 'payments', 'orders', ['order_id'], ['id'])
    op.drop_constraint(None, 'payments', type_='unique')
    op.drop_index(op.f('ix_payments_order_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.create_index('order_id', 'payments', ['order_id'], unique=True)
    op.alter_column('payments', 'status',
               existing_type=sa.String(length=100),
               type_=mysql.VARCHAR(length=50),
               existing_nullable=True)
    op.alter_column('payments', 'order_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.drop_column('payments', 'result_desc')
    op.drop_column('payments', 'result_code')
    op.drop_column('payments', 'transaction_id')
    op.drop_column('payments', 'phone_number')
    op.drop_column('payments', 'merchant_request_id')
    op.drop_column('payments', 'checkout_request_id')
    # ### end Alembic commands ###
