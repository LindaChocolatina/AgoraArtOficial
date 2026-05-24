"""Add banner_perfil to usuarios

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-23

"""
from alembic import op
import sqlalchemy as sa


revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('usuarios', sa.Column('banner_perfil', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('usuarios', 'banner_perfil')
