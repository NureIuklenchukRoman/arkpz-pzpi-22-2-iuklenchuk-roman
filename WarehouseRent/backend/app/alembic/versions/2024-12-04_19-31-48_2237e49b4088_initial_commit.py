"""initial commit

Revision ID: 2237e49b4088
Revises: 
Create Date: 2024-12-04 19:31:48.073590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2237e49b4088'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.Text(), nullable=True),
    sa.Column('email', sa.Text(), nullable=True),
    sa.Column('phone_number', sa.Text(), nullable=True),
    sa.Column('password', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('warehouses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('size_sqm', sa.Float(), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=True),
    sa.Column('price_per_day', sa.Float(), nullable=False),
    sa.Column('premium_services', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_warehouses_id'), 'warehouses', ['id'], unique=False)
    op.create_table('rentals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('warehouse_id', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('total_price', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('RESERVED', 'COMPLETED', 'CANCELLED', name='rentalstatus'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name="fk_rental_user" ),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], name="fk_rental_warehouse" ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rentals_id'), 'rentals', ['id'], unique=False)
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rental_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'COMPLETED', 'FAILED', name='paymentstatus'), nullable=True),
    sa.Column('transaction_id', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['rental_id'], ['rentals.id'], name="fk_payment_rental" ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('transaction_id')
    )
    op.create_index(op.f('ix_payments_id'), 'payments', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_payment_rental', 'payments', type_='foreignkey')
    op.drop_constraint('fk_rental_user', 'rentals', type_='foreignkey')
    op.drop_constraint('fk_rental_warehouse', 'rentals', type_='foreignkey')
    op.drop_index(op.f('ix_payments_id'), table_name='payments')
    op.drop_table('payments')
    op.drop_index(op.f('ix_rentals_id'), table_name='rentals')
    op.drop_table('rentals')
    op.drop_index(op.f('ix_warehouses_id'), table_name='warehouses')
    op.drop_table('warehouses')
    op.drop_table('users')
    # ### end Alembic commands ###