import os
from datetime import timedelta

_BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def _normalize_database_url(url):
    """Adapta DATABASE_URL de Coolify para SQLAlchemy con el driver psycopg v3."""
    if not url:
        return url
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    if url.startswith('postgresql://') and not url.startswith('postgresql+'):
        url = 'postgresql+psycopg://' + url[len('postgresql://'):]
    return url


def database_uri(sqlite_filename):
    """PostgreSQL vía DATABASE_URL (producción) o SQLite local como fallback."""
    url = _normalize_database_url(os.environ.get('DATABASE_URL'))
    if url:
        return url
    return 'sqlite:///' + os.path.join(_BASEDIR, sqlite_filename)


def sqlalchemy_engine_options(uri=None):
    """Opciones del motor: timeout en SQLite para evitar 'database is locked'."""
    uri = uri or database_uri('art_platform.db')
    if uri.startswith('sqlite'):
        return {'connect_args': {'timeout': 30}}
    return {}


class Config:
    """Configuración base de la aplicación"""
    
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Configuración de base de datos
    basedir = _BASEDIR
    SQLALCHEMY_DATABASE_URI = database_uri('art_platform.db')
    SQLALCHEMY_ENGINE_OPTIONS = sqlalchemy_engine_options(SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Configuración de subida de archivos
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    
    # Configuración de paginación
    ITEMS_PER_PAGE = 12

    # Pasarela de pago (Stripe). Sin claves → modo demo en checkout.
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Configuración de correo (newsletters y restablecer contraseña)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME

    # Reset de contraseña: sin SMTP en local → enlace en pantalla (demo)
    PASSWORD_RESET_DEMO = os.environ.get('PASSWORD_RESET_DEMO', '').lower() in ['true', 'on', '1']
    PASSWORD_RESET_MAX_AGE = int(os.environ.get('PASSWORD_RESET_MAX_AGE') or 3600)
    
    @staticmethod
    def init_app(app):
        """Inicialización de configuración"""
        pass

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # Uses SQLALCHEMY_DATABASE_URI from base Config (DATABASE_URL)

class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get('TEST_DATABASE_URL')
    ) or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    basedir = _BASEDIR
    SQLALCHEMY_DATABASE_URI = database_uri('art_platform_prod.db')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Log de errores en producción
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            file_handler = RotatingFileHandler(
                'logs/art_platform.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('Art Platform startup')

# Configuración por entorno
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
