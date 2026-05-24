from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Inicializar extensiones
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def _ensure_dev_schema_patches():
    """Añade columnas/tablas nuevas en BD local sin romper datos existentes."""
    from sqlalchemy import inspect, text
    insp = inspect(db.engine)
    if 'productos' in insp.get_table_names():
        cols = {c['name'] for c in insp.get_columns('productos')}
        if 'moneda' not in cols:
            db.session.execute(text(
                "ALTER TABLE productos ADD COLUMN moneda VARCHAR(3) NOT NULL DEFAULT 'USD'"
            ))
            db.session.commit()
    if 'usuarios' in insp.get_table_names():
        cols = {c['name'] for c in insp.get_columns('usuarios')}
        if 'banner_perfil' not in cols:
            db.session.execute(text(
                "ALTER TABLE usuarios ADD COLUMN banner_perfil VARCHAR(255)"
            ))
            db.session.commit()
        if 'banner_offset' not in cols:
            db.session.execute(text(
                "ALTER TABLE usuarios ADD COLUMN banner_offset INTEGER DEFAULT 50"
            ))
            db.session.commit()


def create_app(config_name='default'):
    """
    Fábrica de aplicaciones Flask
    
    Args:
        config_name (str): Nombre de la configuración ('development', 'testing', 'production')
    
    Returns:
        Flask: Aplicación Flask configurada
    """
    import os
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'), static_folder=os.path.join(basedir, 'static'))
    
    # Cargar configuración
    from app.config.config import config
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Import models so Alembic can detect them
    import app.models as _models
    if config_name == 'development':
        with app.app_context():
            db.create_all()
            _ensure_dev_schema_patches()

    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configurar Login Manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Crear carpetas de uploads si no existen
    import os
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Registrar manejadores de errores
    register_error_handlers(app)
    
    # Registrar filtros de plantilla
    register_template_filters(app)
    register_template_globals(app)
    
    # Cargar usuario para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.usuario import Usuario
        return Usuario.query.get(int(user_id))
    
    return app

def register_blueprints(app):
    """Registrar todos los blueprints de la aplicación"""
    
    # Blueprint de autenticación
    from app.controllers.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Blueprint de artistas
    from app.controllers.artista import artista_bp
    app.register_blueprint(artista_bp, url_prefix='/artista')
    
    # Blueprint de clientes
    from app.controllers.cliente import cliente_bp
    app.register_blueprint(cliente_bp, url_prefix='/cliente')
    
    # Blueprint de administración
    from app.controllers.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Blueprint público (home, explorar, etc.)
    from app.controllers.public import public_bp
    app.register_blueprint(public_bp)
    
    # Blueprint de API (para AJAX y futuras integraciones)
    from app.controllers.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

def register_error_handlers(app):
    """Registrar manejadores de errores personalizados"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('errors/403.html'), 403

def register_template_globals(app):
    @app.template_global()
    def imagenes_obra(obra):
        from app.utils.obra_galeria import listar_imagenes_obra
        return listar_imagenes_obra(obra)

    @app.template_global()
    def contar_imagenes_obra(obra):
        from app.utils.obra_galeria import contar_imagenes_obra as contar
        return contar(obra)


def register_template_filters(app):
    """Registrar filtros personalizados para plantillas"""
    
    @app.template_filter('currency')
    def currency_filter(value):
        """Formatear número como moneda"""
        try:
            return f"${value:,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @app.template_filter('precio_producto')
    def precio_producto_filter(producto):
        """Precio con símbolo según moneda del producto (USD, EUR, COP)."""
        from app.utils.moneda import formatear_precio
        if producto is None:
            return ''
        moneda = getattr(producto, 'moneda', None) or 'USD'
        return formatear_precio(producto.precio, moneda)
    
    @app.template_filter('date')
    def date_filter(value, format='%d/%m/%Y'):
        """Formatear fecha"""
        if value is None:
            return ""
        try:
            return value.strftime(format)
        except (ValueError, TypeError, AttributeError):
            return str(value)
    
    @app.template_filter('truncate_words')
    def truncate_words_filter(s, num_words=20, suffix='...'):
        """Truncar texto por palabras"""
        try:
            words = s.split()
            if len(words) <= num_words:
                return s
            return ' '.join(words[:num_words]) + suffix
        except (ValueError, TypeError):
            return s
