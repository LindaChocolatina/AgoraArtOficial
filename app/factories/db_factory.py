from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from app.config.config import config

class DatabaseFactory:
    """Fábrica para crear y gestionar conexiones a base de datos"""
    
    _engine = None
    _session_factory = None
    
    @classmethod
    def create_engine(cls, database_url=None, config_name='development'):
        """
        Crear motor de base de datos
        
        Args:
            database_url (str): URL de conexión a la base de datos
            config_name (str): Nombre de la configuración
            
        Returns:
            Engine: Motor SQLAlchemy configurado
        """
        if cls._engine is None:
            if database_url is None:
                from app.config.config import config
                database_url = config[config_name].SQLALCHEMY_DATABASE_URI
            
            # Configuración específica para el motor
            engine_kwargs = {
                'pool_pre_ping': True,
                'pool_recycle': 300,
            }
            
            # Para SQLite en pruebas
            if 'sqlite' in database_url:
                engine_kwargs.update({
                    'poolclass': StaticPool,
                    'connect_args': {'check_same_thread': False}
                })
            else:
                engine_kwargs.update({
                    'pool_size': 5,
                    'max_overflow': 10,
                })
            
            cls._engine = create_engine(database_url, **engine_kwargs)
        
        return cls._engine
    
    @classmethod
    def create_session_factory(cls, engine=None):
        """
        Crear fábrica de sesiones
        
        Args:
            engine: Motor SQLAlchemy (opcional)
            
        Returns:
            scoped_session: Fábrica de sesiones con scope
        """
        if cls._session_factory is None:
            if engine is None:
                engine = cls.create_engine()
            
            cls._session_factory = scoped_session(
                sessionmaker(bind=engine, autocommit=False, autoflush=False)
            )
        
        return cls._session_factory
    
    @classmethod
    def get_session(cls):
        """
        Obtener sesión de base de datos
        
        Returns:
            Session: Sesión SQLAlchemy activa
        """
        if cls._session_factory is None:
            cls.create_session_factory()
        
        return cls._session_factory()
    
    @classmethod
    def close_session(cls):
        """Cerrar sesión actual"""
        if cls._session_factory is not None:
            cls._session_factory.remove()
    
    @classmethod
    def reset_factory(cls):
        """Resetear fábrica (útil para pruebas)"""
        if cls._engine is not None:
            cls._engine.dispose()
            cls._engine = None
        
        if cls._session_factory is not None:
            cls._session_factory.remove()
            cls._session_factory = None

class RepositoryFactory:
    """Fábrica para crear repositorios de datos"""
    
    @staticmethod
    def create_repository(model_class, session=None):
        """
        Crear repositorio para un modelo específico
        
        Args:
            model_class: Clase del modelo SQLAlchemy
            session: Sesión de base de datos (opcional)
            
        Returns:
            BaseRepository: Repositorio configurado para el modelo
        """
        from app.repositories.base_repository import BaseRepository
        
        if session is None:
            session = DatabaseFactory.get_session()
        
        return BaseRepository(model_class, session)
    
    @staticmethod
    def create_user_repository(session=None):
        """Crear repositorio de usuarios"""
        from app.models.usuario import Usuario
        from app.repositories.usuario_repository import UsuarioRepository
        
        if session is None:
            session = DatabaseFactory.get_session()
        
        return UsuarioRepository(session)
    
    @staticmethod
    def create_obra_repository(session=None):
        """Crear repositorio de obras"""
        from app.models.obra import Obra
        from app.repositories.obra_repository import ObraRepository
        
        if session is None:
            session = DatabaseFactory.get_session()
        
        return ObraRepository(session)
    
    @staticmethod
    def create_producto_repository(session=None):
        """Crear repositorio de productos"""
        from app.models.producto import Producto
        from app.repositories.producto_repository import ProductoRepository
        
        if session is None:
            session = DatabaseFactory.get_session()
        
        return ProductoRepository(session)
    
    @staticmethod
    def create_categoria_repository(session=None):
        """Crear repositorio de categorías"""
        from app.models.categoria import Categoria
        from app.repositories.categoria_repository import CategoriaRepository
        
        if session is None:
            session = DatabaseFactory.get_session()
        
        return CategoriaRepository(session)

    @staticmethod
    def create_moodboard_repository(session=None):
        """Crear repositorio de moodboards"""
        from app.repositories.moodboard_repository import MoodboardRepository
        
        if session is None:
            session = DatabaseFactory.get_session()
            
        return MoodboardRepository(session)

    @staticmethod
    def create_direccion_repository(session=None):
        """Crear repositorio de direcciones"""
        from app.repositories.direccion_repository import DireccionRepository
        
        if session is None:
            session = DatabaseFactory.get_session()
            
        return DireccionRepository(session)
