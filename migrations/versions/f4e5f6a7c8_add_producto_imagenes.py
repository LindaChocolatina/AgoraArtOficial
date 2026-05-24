"""Add producto_imagenes table

Revision ID: f4e5f6a7c8
Revises: d4e5f6a7b9
Create Date: 2026-05-24

"""
from alembic import op
import sqlalchemy as sa

revision = 'f4e5f6a7c8'
down_revision = 'd4e5f6a7b9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'producto_imagenes',
        sa.Column('id_imagen', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('id_producto', sa.Integer(), nullable=False),
        sa.Column('imagen', sa.String(length=255), nullable=False),
        sa.Column('orden', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_producto'], ['productos.id_producto'], ),
    )


def downgrade():
    op.drop_table('producto_imagenes')
