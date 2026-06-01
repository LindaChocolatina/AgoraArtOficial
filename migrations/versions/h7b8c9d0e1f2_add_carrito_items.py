"""Add carrito_items table

Revision ID: h7b8c9d0e1f2
Revises: g6a7b8c9d0e1
Create Date: 2026-05-31

"""
from alembic import op
import sqlalchemy as sa


revision = 'h7b8c9d0e1f2'
down_revision = 'g6a7b8c9d0e1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'carrito_items',
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('id_producto', sa.Integer(), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['id_producto'], ['productos.id_producto']),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario']),
        sa.PrimaryKeyConstraint('id_usuario', 'id_producto'),
    )


def downgrade():
    op.drop_table('carrito_items')
