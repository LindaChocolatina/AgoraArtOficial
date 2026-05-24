"""Add obra_imagenes gallery table

Revision ID: a1b2c3d4e5f6
Revises: e212a741ce4b
Create Date: 2026-05-23

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = 'e212a741ce4b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'obra_imagenes',
        sa.Column('id_imagen', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('id_obra', sa.Integer(), nullable=False),
        sa.Column('imagen', sa.String(length=255), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id_obra'], ['obras.id_obra'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_imagen'),
    )


def downgrade():
    op.drop_table('obra_imagenes')
