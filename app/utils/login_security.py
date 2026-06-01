"""Protección anti fuerza bruta en login y recuperación de contraseña."""
from datetime import datetime, timedelta

from flask import request

from app.models.login_bloqueo import LoginBloqueo

# Hash bcrypt fijo para igualar tiempo de respuesta cuando el email no existe.
_DUMMY_HASH = (
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'
)


def obtener_ip_cliente():
    """IP real del cliente (respeta proxy reverso en Coolify)."""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()[:45]
    return (request.remote_addr or '0.0.0.0')[:45]


def normalizar_email(email):
    return (email or '').strip().lower()


class LoginSecurityGuard:
    """Control de intentos fallidos por combinación email + IP."""

    def __init__(self, session, max_attempts=5, lockout_minutes=15):
        self.session = session
        self.max_attempts = max_attempts
        self.lockout_minutes = lockout_minutes

    def _obtener_registro(self, email, ip_address):
        return (
            self.session.query(LoginBloqueo)
            .filter_by(email=email, ip_address=ip_address)
            .first()
        )

    def _limpiar_bloqueo_expirado(self, registro):
        if registro.bloqueado_hasta and registro.bloqueado_hasta <= datetime.utcnow():
            registro.intentos = 0
            registro.bloqueado_hasta = None

    def verificar_bloqueo(self, email, ip_address):
        """
        Comprueba si el login está temporalmente bloqueado.

        Returns:
            tuple: (bloqueado: bool, mensaje: str|None)
        """
        email = normalizar_email(email)
        if not email:
            return (False, None)

        registro = self._obtener_registro(email, ip_address)
        if not registro:
            return (False, None)

        self._limpiar_bloqueo_expirado(registro)
        if registro.bloqueado_hasta and registro.bloqueado_hasta > datetime.utcnow():
            minutos = max(
                1,
                int((registro.bloqueado_hasta - datetime.utcnow()).total_seconds() / 60) + 1,
            )
            return (
                True,
                f'Demasiados intentos fallidos. Espera {minutos} minuto(s) antes de volver a intentar.',
            )

        self.session.commit()
        return (False, None)

    def registrar_fallo(self, email, ip_address):
        """Incrementa contador y aplica bloqueo temporal si se supera el límite."""
        email = normalizar_email(email)
        if not email:
            return

        ahora = datetime.utcnow()
        registro = self._obtener_registro(email, ip_address)
        if not registro:
            registro = LoginBloqueo(
                email=email,
                ip_address=ip_address,
                intentos=0,
            )
            self.session.add(registro)

        self._limpiar_bloqueo_expirado(registro)
        registro.intentos += 1
        registro.ultimo_intento = ahora

        if registro.intentos >= self.max_attempts:
            registro.bloqueado_hasta = ahora + timedelta(minutes=self.lockout_minutes)
            registro.intentos = 0

        self.session.commit()

    def limpiar_tras_exito(self, email, ip_address):
        """Elimina el registro tras un login correcto."""
        email = normalizar_email(email)
        if not email:
            return

        registro = self._obtener_registro(email, ip_address)
        if registro:
            self.session.delete(registro)
            self.session.commit()

    @staticmethod
    def dummy_password_hash():
        return _DUMMY_HASH


class PasswordResetRateLimiter:
    """Límite simple por IP en solicitudes de restablecimiento."""

    def __init__(self, session, max_requests=5, window_minutes=60):
        self.session = session
        self.max_requests = max_requests
        self.window_minutes = window_minutes

    def _clave_ip(self, ip_address):
        return f'__reset_ip__:{ip_address}'

    def permitido(self, ip_address):
        clave = self._clave_ip(ip_address)
        registro = self.session.query(LoginBloqueo).filter_by(email=clave, ip_address=ip_address).first()
        if not registro:
            return True

        ventana = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        if registro.ultimo_intento < ventana:
            self.session.delete(registro)
            self.session.commit()
            return True

        return registro.intentos < self.max_requests

    def registrar_solicitud(self, ip_address):
        clave = self._clave_ip(ip_address)
        ahora = datetime.utcnow()
        registro = self.session.query(LoginBloqueo).filter_by(email=clave, ip_address=ip_address).first()
        ventana = ahora - timedelta(minutes=self.window_minutes)

        if registro and registro.ultimo_intento < ventana:
            self.session.delete(registro)
            registro = None

        if not registro:
            registro = LoginBloqueo(email=clave, ip_address=ip_address, intentos=0)
            self.session.add(registro)

        registro.intentos += 1
        registro.ultimo_intento = ahora
        self.session.commit()
