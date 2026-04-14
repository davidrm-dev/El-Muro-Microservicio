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
    # Create materias table
    op.create_table(
        'materias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('semestre', sa.Integer(), nullable=False),
        sa.Column('carrera_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_materia_nombre', 'materias', ['nombre'])
    op.create_index('idx_materia_carrera_id', 'materias', ['carrera_id'])
    op.create_index('idx_materia_semestre', 'materias', ['semestre'])
    
    # Create temas table
    op.create_table(
        'temas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(255), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('materia_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['materia_id'], ['materias.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_tema_nombre', 'temas', ['nombre'])
    op.create_index('idx_tema_materia', 'temas', ['materia_id'])


def downgrade() -> None:
    op.drop_table('temas')
    op.drop_table('materias')
