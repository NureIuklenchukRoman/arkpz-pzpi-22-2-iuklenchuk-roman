"""add is_deleted to warehouse_

Revision ID: 624ceed9e148
Revises: bb356b4fff0c
Create Date: 2024-12-18 13:49:15.866942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '624ceed9e148'
down_revision: Union[str, None] = 'bb356b4fff0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('warehouses', sa.Column('is_deleted', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('warehouses', 'is_deleted')
    # ### end Alembic commands ###