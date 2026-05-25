"""Fábrica de servicios para la aplicación"""

class ServiceFactory:
    """Fábrica centralizada para crear servicios de negocio"""
    
    def __init__(self, session=None):
        """
        Inicializar fábrica de servicios
        
        Args:
            session: Sesión de base de datos (opcional)
        """
        self.session = session
        self._services = {}
    
    def get_auth_service(self):
        """Obtener servicio de autenticación"""
        if 'auth' not in self._services:
            from app.services.auth_service import AuthService
            from app.factories.db_factory import RepositoryFactory
            
            user_repo = RepositoryFactory.create_user_repository(self.session)
            self._services['auth'] = AuthService(user_repo)
        
        return self._services['auth']
    
    def get_usuario_service(self):
        """Obtener servicio de usuarios"""
        if 'usuario' not in self._services:
            from app.services.usuario_service import UsuarioService
            from app.factories.db_factory import RepositoryFactory
            
            user_repo = RepositoryFactory.create_user_repository(self.session)
            self._services['usuario'] = UsuarioService(user_repo)
        
        return self._services['usuario']
    
    def get_usuario_repository(self):
        """Obtener repositorio de usuarios"""
        from app.factories.db_factory import RepositoryFactory
        return RepositoryFactory.create_user_repository(self.session)
    
    def get_obra_service(self):
        """Obtener servicio de obras"""
        if 'obra' not in self._services:
            from app.services.obra_service import ObraService
            from app.factories.db_factory import RepositoryFactory
            
            obra_repo = RepositoryFactory.create_obra_repository(self.session)
            categoria_repo = RepositoryFactory.create_categoria_repository(self.session)
            self._services['obra'] = ObraService(obra_repo, categoria_repo)
        
        return self._services['obra']
    
    def get_producto_service(self):
        """Obtener servicio de productos"""
        if 'producto' not in self._services:
            from app.services.producto_service import ProductoService
            from app.factories.db_factory import RepositoryFactory
            
            producto_repo = RepositoryFactory.create_producto_repository(self.session)
            self._services['producto'] = ProductoService(producto_repo)
        
        return self._services['producto']
    
    def get_categoria_service(self):
        """Obtener servicio de categorías"""
        if 'categoria' not in self._services:
            from app.services.categoria_service import CategoriaService
            from app.factories.db_factory import RepositoryFactory
            
            categoria_repo = RepositoryFactory.create_categoria_repository(self.session)
            self._services['categoria'] = CategoriaService(categoria_repo)
        
        return self._services['categoria']
    
    def get_carrito_service(self):
        """Obtener servicio de carrito"""
        if 'carrito' not in self._services:
            from app.services.carrito_service import CarritoService
            from app.factories.db_factory import RepositoryFactory
            
            producto_repo = RepositoryFactory.create_producto_repository(self.session)
            self._services['carrito'] = CarritoService(producto_repo)
        
        return self._services['carrito']
    
    def get_orden_service(self):
        """Obtener servicio de órdenes"""
        if 'orden' not in self._services:
            from app.services.orden_service import OrdenService
            session = self.session
            if session is None:
                from app.factories.db_factory import DatabaseFactory
                session = DatabaseFactory.get_session()
            self._services['orden'] = OrdenService(session)
        
        return self._services['orden']
    
    def get_blog_service(self):
        """Obtener servicio de blog"""
        if 'blog' not in self._services:
            from app.services.blog_service import BlogService
            self._services['blog'] = BlogService()
        
        return self._services['blog']
    
    def get_newsletter_service(self):
        """Obtener servicio de newsletters"""
        if 'newsletter' not in self._services:
            from app.services.newsletter_service import NewsletterService
            session = self.session
            if session is None:
                from app.factories.db_factory import DatabaseFactory
                session = DatabaseFactory.get_session()
            self._services['newsletter'] = NewsletterService(session)
        
        return self._services['newsletter']
    
    def get_moodboard_service(self):
        """Obtener servicio de moodboards"""
        if 'moodboard' not in self._services:
            from app.services.moodboard_service import MoodboardService
            from app.factories.db_factory import RepositoryFactory
            
            mood_repo = RepositoryFactory.create_moodboard_repository(self.session)
            obra_repo = RepositoryFactory.create_obra_repository(self.session)
            self._services['moodboard'] = MoodboardService(mood_repo, obra_repo)
            
        return self._services['moodboard']

    def get_direccion_service(self):
        """Obtener servicio de direcciones"""
        if 'direccion' not in self._services:
            from app.services.direccion_service import DireccionService
            from app.factories.db_factory import RepositoryFactory
            
            dir_repo = RepositoryFactory.create_direccion_repository(self.session)
            self._services['direccion'] = DireccionService(dir_repo)
            
        return self._services['direccion']

    def get_payment_service(self):
        """Obtener servicio de pagos"""
        if 'payment' not in self._services:
            from app.services.payment_service import PaymentService
            from flask import current_app
            self._services['payment'] = PaymentService(self.session, current_app.config)
        return self._services['payment']

    def get_admin_service(self):
        """Obtener servicio de administración"""
        if 'admin' not in self._services:
            from app.services.admin_service import AdminService
            from app.factories.db_factory import RepositoryFactory
            
            user_repo = RepositoryFactory.create_user_repository(self.session)
            obra_repo = RepositoryFactory.create_obra_repository(self.session)
            producto_repo = RepositoryFactory.create_producto_repository(self.session)
            
            self._services['admin'] = AdminService(user_repo, obra_repo, producto_repo)
        
        return self._services['admin']

def get_service_factory(session=None):
    """
    Función de conveniencia para obtener una instancia de ServiceFactory
    
    Args:
        session: Sesión de base de datos (opcional)
    
    Returns:
        ServiceFactory: Instancia de la fábrica de servicios
    """
    if session is None:
        from app.factories.app_factory import db
        session = db.session
    return ServiceFactory(session)
