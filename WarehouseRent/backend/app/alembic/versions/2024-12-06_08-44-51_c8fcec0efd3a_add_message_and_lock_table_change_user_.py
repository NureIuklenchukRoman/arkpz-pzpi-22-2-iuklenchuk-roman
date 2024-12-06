"""Add message and lock table change user table

Revision ID: c8fcec0efd3a
Revises: 2237e49b4088
Create Date: 2024-12-06 08:44:51.085227

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8fcec0efd3a'
down_revision: Union[str, None] = '2237e49b4088'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the 'userrole' enum type
    userrole_enum = sa.Enum('ADMIN', 'CUSTOMER', name='userrole')
    userrole_enum.create(op.get_bind())

    # Add new columns and create tables
    op.create_table(
        'locks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('access_key', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locks_id'), 'locks', ['id'], unique=False)
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)
    op.add_column('users', sa.Column('username', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('role', sa.Enum('ADMIN', 'CUSTOMER', name='userrole'), nullable=True))
    op.drop_column('users', 'name')



def downgrade() -> None:
    op.add_column('users', sa.Column('name', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_column('users', 'role')
    op.drop_column('users', 'username')
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_locks_id'), table_name='locks')
    op.drop_table('locks')

    # Drop the 'userrole' enum type
    userrole_enum = sa.Enum('ADMIN', 'CUSTOMER', name='userrole')
    userrole_enum.drop(op.get_bind())

