"""Initial migration

Revision ID: 001
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create carreras table
    op.create_table(
        'carreras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre'),
    )
    op.create_index('idx_carrera_nombre', 'carreras', ['nombre'])


def downgrade() -> None:
    op.drop_table('carreras')
