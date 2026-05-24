"""Add moneda column to productos

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-05-23

"""
from alembic import op
import sqlalchemy as sa


revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'productos',
        sa.Column('moneda', sa.String(length=3), nullable=False, server_default='USD'),
    )


def downgrade():
    op.drop_column('productos', 'moneda')
