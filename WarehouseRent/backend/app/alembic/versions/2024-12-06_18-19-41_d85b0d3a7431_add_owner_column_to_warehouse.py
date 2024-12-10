"""add owner column to warehouse

Revision ID: d85b0d3a7431
Revises: c8fcec0efd3a
Create Date: 2024-12-06 18:19:41.005180

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd85b0d3a7431'
down_revision: Union[str, None] = 'c8fcec0efd3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the 'owned_by' column
    op.add_column('warehouses', sa.Column('owned_by', sa.Integer(), nullable=False))
    # Create a foreign key constraint with an explicit name
    op.create_foreign_key('fk_warehouses_owned_by', 'warehouses', 'users', ['owned_by'], ['id'])


def downgrade() -> None:
    # Drop the foreign key constraint by name
    op.drop_constraint('fk_warehouses_owned_by', 'warehouses', type_='foreignkey')
    # Drop the 'owned_by' column
    op.drop_column('warehouses', 'owned_by')
