"""
Servicio de gestión de productos
Maneja operaciones de negocio relacionadas con productos y e-commerce
"""

class ProductoService:
    """
    Servicio de productos para operaciones de negocio
    """
    
    def __init__(self, producto_repository):
        """
        Inicializar servicio de productos
        
        Args:
            producto_repository: Repositorio de productos
        """
        self.producto_repo = producto_repository
    
    def get_by_id(self, producto_id):
        """
        Obtener producto por ID
        
        Args:
            producto_id (int): ID del producto
            
        Returns:
            Producto: Instancia del producto o None
        """
        return self.producto_repo.get_by_id(producto_id)
    
    def get_all(self, filters=None, limit=None, offset=None):
        """
        Obtener todos los productos con filtros opcionales
        
        Args:
            filters (dict): Filtros a aplicar
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de productos
        """
        return self.producto_repo.get_all(filters=filters, limit=limit, offset=offset)
    
    def get_by_artista(self, artista_id, disponibles_only=True, limit=None, offset=None):
        """
        Obtener productos de un artista
        
        Args:
            artista_id (int): ID del artista
            disponibles_only (bool): Solo productos con stock
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de productos del artista
        """
        return self.producto_repo.get_by_artista(artista_id, disponibles_only=disponibles_only, limit=limit, offset=offset)
    
    def get_count_by_artista(self, artista_id, disponibles_only=True):
        """
        Obtener cantidad de productos de un artista
        
        Args:
            artista_id (int): ID del artista
            disponibles_only (bool): Solo productos con stock
            
        Returns:
            int: Cantidad de productos
        """
        return self.producto_repo.get_count_by_artista(artista_id, disponibles_only=disponibles_only)
    
    def get_disponibles(self, limit=None, offset=None):
        """
        Obtener productos disponibles (con stock)
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de productos disponibles
        """
        return self.producto_repo.get_disponibles(limit=limit, offset=offset)
    
    def get_agotados(self, limit=None, offset=None):
        """
        Obtener productos agotados
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de productos agotados
        """
        return self.producto_repo.get_agotados(limit=limit, offset=offset)
    
    def buscar_productos(self, termino, disponibles_only=True, limit=None):
        """
        Buscar productos por nombre o descripción
        
        Args:
            termino (str): Término de búsqueda
            disponibles_only (bool): Solo productos con stock
            limit (int): Límite de resultados
            
        Returns:
            list: Lista de productos que coinciden
        """
        return self.producto_repo.buscar_productos(termino, disponibles_only=disponibles_only, limit=limit)
    
    def crear_producto(self, data, usuario_id=None):
        """
        Crear nuevo producto
        
        Args:
            data (dict): Datos del producto
            usuario_id (int): ID del usuario que crea
            
        Returns:
            tuple: (bool, Producto) - (exitoso, producto_creado)
        """
        # Validar datos
        if not data.get('nombre', '').strip():
            return (False, None)
        
        if not data.get('id_artista'):
            return (False, None)
        
        if not data.get('precio') or data['precio'] <= 0:
            return (False, None)
        
        # Crear producto
        producto = self.producto_repo.create(data)
        
        if producto:
            self.producto_repo.save()
            return (True, producto)
        
        return (False, None)
    
    def actualizar_producto(self, producto_id, data, usuario_id=None):
        """
        Actualizar producto existente
        
        Args:
            producto_id (int): ID del producto
            data (dict): Datos a actualizar
            usuario_id (int): ID del usuario que actualiza
            
        Returns:
            tuple: (bool, Producto) - (exitoso, producto_actualizado)
        """
        # Validar datos
        if 'nombre' in data and not data['nombre'].strip():
            return (False, None)
        
        if 'precio' in data and (not data['precio'] or data['precio'] <= 0):
            return (False, None)
        
        # Actualizar producto
        producto_actualizado = self.producto_repo.update(producto_id, data, usuario_id)
        
        if producto_actualizado:
            self.producto_repo.save()
            return (True, producto_actualizado)
        
        return (False, None)
    
    def actualizar_stock(self, producto_id, cantidad, motivo=None, usuario_id=None):
        """
        Actualizar stock de un producto
        
        Args:
            producto_id (int): ID del producto
            cantidad (int): Cantidad a agregar (positivo) o reducir (negativo)
            motivo (str): Motivo del cambio
            usuario_id (int): ID del usuario que realiza la acción
            
        Returns:
            Producto: Producto actualizado o None si hay error
        """
        return self.producto_repo.actualizar_stock(producto_id, cantidad, motivo, usuario_id)
    
    def reducir_stock_venta(self, producto_id, cantidad):
        """
        Reducir stock por venta
        
        Args:
            producto_id (int): ID del producto
            cantidad (int): Cantidad a reducir
            
        Returns:
            bool: True si se redujo correctamente, False si no hay stock suficiente
        """
        return self.producto_repo.reducir_stock_venta(producto_id, cantidad)
    
    def get_historial_stock(self, producto_id, limit=None):
        """
        Obtener historial de cambios de stock de un producto
        
        Args:
            producto_id (int): ID del producto
            limit (int): Límite de resultados
            
        Returns:
            list: Lista de registros de historial
        """
        return self.producto_repo.get_historial_stock(producto_id, limit=limit)
    
    def get_mas_vendidos(self, limit=None):
        """
        Obtener productos más vendidos
        
        Args:
            limit (int): Límite de resultados
            
        Returns:
            list: Lista de productos más vendidos
        """
        return self.producto_repo.get_mas_vendidos(limit=limit)
    
    def get_precio_range(self, artista_id=None):
        """
        Obtener rango de precios
        
        Args:
            artista_id (int): ID del artista (opcional)
            
        Returns:
            tuple: (precio_min, precio_max)
        """
        return self.producto_repo.get_precio_range(artista_id=artista_id)
    
    def count(self, filters=None):
        """
        Contar productos con filtros opcionales
        
        Args:
            filters (dict): Filtros a aplicar
            
        Returns:
            int: Cantidad de productos
        """
        return self.producto_repo.count(filters=filters)
    
    def eliminar_producto(self, producto_id, usuario_id=None):
        """Eliminar producto de la base de datos."""
        producto = self.producto_repo.get_by_id(producto_id)
        if not producto:
            return False
        if producto.orden_items.count() > 0:
            return False
        session = self.producto_repo.session
        try:
            from app.models.producto import HistorialStock
            session.query(HistorialStock).filter_by(id_producto=producto_id).delete(
                synchronize_session=False
            )
            if not self.producto_repo.delete(producto_id, usuario_id):
                session.rollback()
                return False
            return self.producto_repo.save()
        except Exception as e:
            session.rollback()
            print(f"Error al eliminar producto {producto_id}: {e}")
            return False
    
    def get_estadisticas_artista(self, artista_id):
        """
        Obtener estadísticas de productos de un artista
        
        Args:
            artista_id (int): ID del artista
            
        Returns:
            dict: Estadísticas del artista
        """
        total_productos = self.get_count_by_artista(artista_id, disponibles_only=False)
        productos_disponibles = self.get_count_by_artista(artista_id, disponibles_only=True)
        productos_agotados = total_productos - productos_disponibles
        
        precio_min, precio_max = self.get_precio_range(artista_id)
        
        return {
            'total_productos': total_productos,
            'productos_disponibles': productos_disponibles,
            'productos_agotados': productos_agotados,
            'precio_minimo': precio_min,
            'precio_maximo': precio_max
        }
    
    def get_estadisticas_generales(self):
        """
        Obtener estadísticas generales de productos
        
        Returns:
            dict: Estadísticas generales
        """
        total_productos = self.count()
        productos_disponibles = len(self.get_disponibles())
        productos_agotados = len(self.get_agotados())
        
        precio_min, precio_max = self.get_precio_range()
        
        return {
            'total_productos': total_productos,
            'productos_disponibles': productos_disponibles,
            'productos_agotados': productos_agotados,
            'precio_minimo': precio_min,
            'precio_maximo': precio_max
        }
    
    def verificar_disponibilidad(self, producto_id, cantidad_solicitada):
        """
        Verificar si hay suficiente stock para una cantidad solicitada
        
        Args:
            producto_id (int): ID del producto
            cantidad_solicitada (int): Cantidad solicitada
            
        Returns:
            bool: True si hay stock suficiente
        """
        producto = self.get_by_id(producto_id)
        
        if not producto:
            return False
        
        return producto.stock >= cantidad_solicitada
    
    def get_productos_bajo_stock(self, umbral=5):
        """
        Obtener productos con stock bajo
        
        Args:
            umbral (int): Umbral de stock bajo
            
        Returns:
            list: Lista de productos con stock bajo
        """
        # Implementar lógica para obtener productos con stock bajo
        # Esto requeriría un método en el repositorio
        productos = self.get_all()
        productos_bajo_stock = [p for p in productos if 0 < p.stock < umbral]
        
        return productos_bajo_stock
