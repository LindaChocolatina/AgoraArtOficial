from datetime import datetime

from app.factories.app_factory import db


class LoginBloqueo(db.Model):
    """Intentos fallidos de login por email + IP (anti fuerza bruta)."""

    __tablename__ = 'login_bloqueos'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(150), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    intentos = db.Column(db.Integer, nullable=False, default=0)
    bloqueado_hasta = db.Column(db.DateTime, nullable=True)
    ultimo_intento = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('email', 'ip_address', name='uq_login_bloqueo_email_ip'),
    )
