"""Tokens firmados para restablecer contraseña."""
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

SALT = 'agora-art-password-reset'
MAX_AGE_SECONDS = 3600  # 1 hora


def _serializer(secret_key):
    return URLSafeTimedSerializer(secret_key, salt=SALT)


def generar_token_reset(secret_key, user_id):
    return _serializer(secret_key).dumps({'uid': int(user_id)})


def verificar_token_reset(secret_key, token, max_age=MAX_AGE_SECONDS):
    try:
        data = _serializer(secret_key).loads(token, max_age=max_age)
        return int(data['uid'])
    except (BadSignature, SignatureExpired, TypeError, ValueError, KeyError):
        return None
