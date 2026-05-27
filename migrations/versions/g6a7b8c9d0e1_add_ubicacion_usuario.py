"""Add ubicacion to usuarios

Revision ID: g6a7b8c9d0e1
Revises: f4e5f6a7c8
Create Date: 2026-05-23

"""
from alembic import op
import sqlalchemy as sa


revision = 'g6a7b8c9d0e1'
down_revision = 'f4e5f6a7c8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('usuarios', sa.Column('ubicacion', sa.String(length=150), nullable=True))


def downgrade():
    op.drop_column('usuarios', 'ubicacion')
