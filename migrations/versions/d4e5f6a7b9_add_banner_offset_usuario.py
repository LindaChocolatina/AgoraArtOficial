"""Add banner_offset to usuarios

Revision ID: d4e5f6a7b9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-24

"""
from alembic import op
import sqlalchemy as sa


revision = 'd4e5f6a7b9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('usuarios', sa.Column('banner_offset', sa.Integer(), nullable=True, server_default='50'))


def downgrade():
    op.drop_column('usuarios', 'banner_offset')
