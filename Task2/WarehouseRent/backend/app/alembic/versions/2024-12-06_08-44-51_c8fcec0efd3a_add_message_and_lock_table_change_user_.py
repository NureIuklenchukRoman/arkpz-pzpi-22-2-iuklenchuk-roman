from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from app.database import UserRole  # Ensure this import points to where UserRole is defined

# revision identifiers, used by Alembic.
revision: str = 'c8fcec0efd3a'
down_revision: Union[str, None] = '2237e49b4088'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the 'userrole' enum type in PostgreSQL
    user_role_enum = sa.Enum(UserRole, name='userrole')
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns and create tables
    op.create_table(
        'locks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.Integer(), nullable=False),
        sa.Column('access_key', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], name="fk_lock_warehouse"),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locks_id'), 'locks', ['id'], unique=False)

    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name="fk_message_user"),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'], unique=False)

    op.add_column('users', sa.Column('username', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('role', user_role_enum, nullable=True))
    op.drop_column('users', 'name')


def downgrade() -> None:
    # Drop the 'role' column and the 'userrole' enum type
    op.drop_column('users', 'role')
    user_role_enum = sa.Enum(UserRole, name='userrole')
    user_role_enum.drop(op.get_bind(), checkfirst=True)

    # Rollback the schema changes
    op.add_column('users', sa.Column('name', sa.TEXT(), autoincrement=False, nullable=True))
    op.drop_constraint('fk_lock_warehouse', 'locks', type_='foreignkey')
    op.drop_constraint('fk_message_user', 'messages', type_='foreignkey')
    op.drop_index(op.f('ix_messages_id'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_locks_id'), table_name='locks')
    op.drop_table('locks')
