"""Add login_bloqueos table for brute-force protection

Revision ID: i8c9d0e1f2a3
Revises: h7b8c9d0e1f2
Create Date: 2026-05-31

"""
from alembic import op
import sqlalchemy as sa


revision = 'i8c9d0e1f2a3'
down_revision = 'h7b8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'login_bloqueos',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=False),
        sa.Column('intentos', sa.Integer(), nullable=False),
        sa.Column('bloqueado_hasta', sa.DateTime(), nullable=True),
        sa.Column('ultimo_intento', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', 'ip_address', name='uq_login_bloqueo_email_ip'),
    )
    op.create_index('ix_login_bloqueos_email', 'login_bloqueos', ['email'])
    op.create_index('ix_login_bloqueos_ip_address', 'login_bloqueos', ['ip_address'])


def downgrade():
    op.drop_index('ix_login_bloqueos_ip_address', table_name='login_bloqueos')
    op.drop_index('ix_login_bloqueos_email', table_name='login_bloqueos')
    op.drop_table('login_bloqueos')
