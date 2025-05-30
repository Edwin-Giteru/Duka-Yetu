"""updates

Revision ID: 9910c3c1f26b
Revises: c61550b09eb3
Create Date: 2025-05-27 15:19:52.400893

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '9910c3c1f26b'
down_revision: Union[str, None] = 'c61550b09eb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order_items', sa.Column('order_id', sa.Integer(), nullable=True))
    op.add_column('order_items', sa.Column('product_id', sa.Integer(), nullable=False))
    op.add_column('order_items', sa.Column('quantity', sa.Integer(), nullable=False))
    op.add_column('order_items', sa.Column('price_per_item', sa.Float(), nullable=False))
    op.drop_index('ix_order_items_user_id', table_name='order_items')
    op.create_foreign_key(None, 'order_items', 'users', ['user_id'], ['id'])
    op.create_foreign_key(None, 'order_items', 'products', ['product_id'], ['id'])
    op.create_foreign_key(None, 'order_items', 'orders', ['order_id'], ['id'])
    op.drop_column('order_items', 'updated_at')
    op.drop_column('order_items', 'total_amount')
    op.drop_column('order_items', 'mpesa_transaction_id')
    op.drop_column('order_items', 'payment_status')
    op.drop_column('order_items', 'created_at')
    op.drop_column('order_items', 'mpesa_checkout_request_id')
    op.drop_column('order_items', 'status')
    op.add_column('orders', sa.Column('total_amount', sa.Float(), nullable=False))
    op.add_column('orders', sa.Column('mpesa_checkout_request_id', sa.String(length=100), nullable=True))
    op.add_column('orders', sa.Column('mpesa_transaction_id', sa.String(length=100), nullable=True))
    op.add_column('orders', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.alter_column('orders', 'user_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.alter_column('orders', 'status',
               existing_type=mysql.ENUM('PENDING', 'COMPLETED', 'CANCELLED'),
               type_=sa.String(length=100),
               nullable=True)
    op.alter_column('orders', 'created_at',
               existing_type=mysql.DATETIME(),
               nullable=True)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)
    op.drop_constraint('orders_ibfk_1', 'orders', type_='foreignkey')
    op.drop_column('orders', 'total_price')
    op.drop_column('orders', 'delivery_address')
    op.drop_constraint('payments_ibfk_3', 'payments', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('payments_ibfk_3', 'payments', 'orders', ['order_id'], ['id'])
    op.add_column('orders', sa.Column('delivery_address', mysql.VARCHAR(length=100), nullable=False))
    op.add_column('orders', sa.Column('total_price', mysql.FLOAT(), nullable=False))
    op.create_foreign_key('orders_ibfk_1', 'orders', 'users', ['user_id'], ['id'])
    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.alter_column('orders', 'created_at',
               existing_type=mysql.DATETIME(),
               nullable=False)
    op.alter_column('orders', 'status',
               existing_type=sa.String(length=100),
               type_=mysql.ENUM('PENDING', 'COMPLETED', 'CANCELLED'),
               nullable=False)
    op.alter_column('orders', 'user_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.drop_column('orders', 'updated_at')
    op.drop_column('orders', 'mpesa_transaction_id')
    op.drop_column('orders', 'mpesa_checkout_request_id')
    op.drop_column('orders', 'total_amount')
    op.add_column('order_items', sa.Column('status', mysql.VARCHAR(length=120), nullable=True))
    op.add_column('order_items', sa.Column('mpesa_checkout_request_id', mysql.VARCHAR(length=200), nullable=True))
    op.add_column('order_items', sa.Column('created_at', mysql.DATETIME(), nullable=True))
    op.add_column('order_items', sa.Column('payment_status', mysql.VARCHAR(length=100), nullable=True))
    op.add_column('order_items', sa.Column('mpesa_transaction_id', mysql.VARCHAR(length=100), nullable=True))
    op.add_column('order_items', sa.Column('total_amount', mysql.FLOAT(), nullable=False))
    op.add_column('order_items', sa.Column('updated_at', mysql.DATETIME(), nullable=True))
    op.drop_constraint(None, 'order_items', type_='foreignkey')
    op.drop_constraint(None, 'order_items', type_='foreignkey')
    op.drop_constraint(None, 'order_items', type_='foreignkey')
    op.create_index('ix_order_items_user_id', 'order_items', ['user_id'], unique=False)
    op.drop_column('order_items', 'price_per_item')
    op.drop_column('order_items', 'quantity')
    op.drop_column('order_items', 'product_id')
    op.drop_column('order_items', 'order_id')
    # ### end Alembic commands ###
