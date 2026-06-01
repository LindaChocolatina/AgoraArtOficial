"""
Servicio de gestión de obras
Maneja operaciones de negocio relacionadas con obras artísticas
"""

class ObraService:
    """
    Servicio de obras para operaciones de negocio
    """
    
    def __init__(self, obra_repository, categoria_repository):
        """
        Inicializar servicio de obras
        
        Args:
            obra_repository: Repositorio de obras
            categoria_repository: Repositorio de categorías
        """
        self.obra_repo = obra_repository
        self.categoria_repo = categoria_repository
    
    def get_by_id(self, obra_id):
        """
        Obtener obra por ID
        
        Args:
            obra_id (int): ID de la obra
            
        Returns:
            Obra: Instancia de la obra o None
        """
        return self.obra_repo.get_by_id(obra_id)
    
    def get_all(self, filters=None, limit=None, offset=None):
        """
        Obtener todas las obras con filtros opcionales
        
        Args:
            filters (dict): Filtros a aplicar
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de obras
        """
        return self.obra_repo.get_all(filters=filters, limit=limit, offset=offset)
    
    def get_by_artista(self, artista_id, visible_only=True, limit=None, offset=None):
        """
        Obtener obras de un artista
        
        Args:
            artista_id (int): ID del artista
            visible_only (bool): Solo obras visibles
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de obras del artista
        """
        return self.obra_repo.get_by_artista(artista_id, visible_only=visible_only, limit=limit, offset=offset)
    
    def get_count_by_artista(self, artista_id, visible_only=True):
        """
        Obtener cantidad de obras de un artista
        
        Args:
            artista_id (int): ID del artista
            visible_only (bool): Solo obras visibles
            
        Returns:
            int: Cantidad de obras
        """
        return self.obra_repo.get_count_by_artista(artista_id, visible_only=visible_only)
    
    def buscar_obras(self, termino, limit=None, offset=None):
        """
        Buscar obras por término
        
        Args:
            termino (str): Término de búsqueda
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de obras que coinciden
        """
        return self.obra_repo.buscar_obras(termino, limit=limit, offset=offset)
    
    def get_obras_recientes(self, limit=None, offset=None):
        """
        Obtener obras recientes
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de obras recientes
        """
        return self.obra_repo.get_obras_recientes(limit=limit)
    
    def get_publicas(self, limit=None, offset=None, categoria_id=None, artista_id=None):
        """
        Obtener obras públicas (visibles)
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            categoria_id (int): Filtrar por categoría
            artista_id (int): Filtrar por artista
            
        Returns:
            list: Lista de obras públicas
        """
        filters = {'visible': True}
        if categoria_id:
            filters['id_categoria'] = categoria_id
        if artista_id:
            filters['id_artista'] = artista_id
        
        return self.obra_repo.get_all(filters=filters, limit=limit, offset=offset)
    
    def crear_obra(self, data, usuario_id=None):
        """
        Crear nueva obra
        
        Args:
            data (dict): Datos de la obra
            usuario_id (int): ID del usuario que crea
            
        Returns:
            tuple: (bool, Obra) - (exitoso, obra_creada)
        """
        # Validar datos
        if not data.get('titulo', '').strip():
            return (False, None)
        
        if not data.get('id_artista'):
            return (False, None)
        
        # Crear obra
        obra = self.obra_repo.create(data)
        
        if obra:
            self.obra_repo.save()
            return (True, obra)
        
        return (False, None)
    
    def actualizar_obra(self, obra_id, data, usuario_id=None):
        """
        Actualizar obra existente
        
        Args:
            obra_id (int): ID de la obra
            data (dict): Datos a actualizar
            usuario_id (int): ID del usuario que actualiza
            
        Returns:
            tuple: (bool, Obra) - (exitoso, obra_actualizada)
        """
        # Validar datos
        if 'titulo' in data and not data['titulo'].strip():
            return (False, None)
        
        # Actualizar obra
        obra_actualizada = self.obra_repo.update(obra_id, data, usuario_id)
        
        if obra_actualizada:
            self.obra_repo.save()
            return (True, obra_actualizada)
        
        return (False, None)
    
    def toggle_visibilidad(self, obra_id, usuario_id=None):
        """
        Cambiar visibilidad de obra
        
        Args:
            obra_id (int): ID de la obra
            usuario_id (int): ID del usuario que modifica
            
        Returns:
            tuple: (bool, Obra) - (exitoso, obra_actualizada)
        """
        obra = self.obra_repo.get_by_id(obra_id)
        if not obra:
            return (False, None)
        
        nueva_visibilidad = not obra.visible
        
        return self.actualizar_obra(obra_id, {'visible': nueva_visibilidad}, usuario_id)
    
    def eliminar_obra(self, obra_id, usuario_id=None):
        """Eliminar obra de la base de datos (y dependencias)."""
        obra = self.obra_repo.get_by_id(obra_id)
        if not obra:
            return False
        session = self.obra_repo.session
        try:
            from app.models.usuario import favoritos_obras
            session.execute(
                favoritos_obras.delete().where(favoritos_obras.c.id_obra == obra_id)
            )
            if not self.obra_repo.delete(obra_id, usuario_id):
                session.rollback()
                return False
            return self.obra_repo.save()
        except Exception as e:
            session.rollback()
            print(f"Error al eliminar obra {obra_id}: {e}")
            return False
    
    def agregar_favorito(self, usuario_id, obra_id):
        """
        Agregar obra a favoritos de usuario
        """
        result = self.obra_repo.agregar_favorito(usuario_id, obra_id)
        if result:
            self.obra_repo.save()
        return result
    
    def quitar_favorito(self, usuario_id, obra_id):
        """
        Quitar obra de favoritos de usuario
        """
        result = self.obra_repo.quitar_favorito(usuario_id, obra_id)
        if result:
            self.obra_repo.save()
        return result
    
    def es_favorito(self, usuario_id, obra_id):
        """
        Verificar si una obra es favorita de un usuario
        
        Args:
            usuario_id (int): ID del usuario
            obra_id (int): ID de la obra
            
        Returns:
            bool: True si es favorita
        """
        return self.obra_repo.es_favorito(usuario_id, obra_id)
    
    def get_favoritos_usuario(self, usuario_id, limit=None, offset=None):
        """
        Obtener obras favoritas de un usuario
        
        Args:
            usuario_id (int): ID del usuario
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de obras favoritas
        """
        return self.obra_repo.get_favoritos_usuario(usuario_id, limit=limit, offset=offset)
    
    def get_favoritos_count(self, usuario_id):
        """
        Obtener cantidad de obras favoritas de un usuario
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            int: Cantidad de obras favoritas
        """
        return self.obra_repo.get_favoritos_count(usuario_id)
    
    def get_artistas_con_obras(self, limit=None, offset=None):
        """
        Obtener artistas que tienen obras
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de artistas con obras
        """
        return self.obra_repo.get_artistas_con_obras(limit=limit)
    
    def count(self, filters=None):
        """
        Contar obras con filtros opcionales
        
        Args:
            filters (dict): Filtros a aplicar
            
        Returns:
            int: Cantidad de obras
        """
        return self.obra_repo.count(filters=filters)
    
    def get_obras_por_categoria(self, categoria_id, limit=None, offset=None):
        """
        Obtener obras por categoría
        
        Args:
            categoria_id (int): ID de la categoría
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de obras de la categoría
        """
        return self.obra_repo.get_by_categoria(categoria_id, limit=limit, offset=offset)
    
    def get_estadisticas_artista(self, artista_id):
        """
        Obtener estadísticas de obras de un artista
        
        Args:
            artista_id (int): ID del artista
            
        Returns:
            dict: Estadísticas del artista
        """
        total_obras = self.get_count_by_artista(artista_id, visible_only=False)
        obras_visibles = self.get_count_by_artista(artista_id, visible_only=True)
        total_favoritos = self.obra_repo.get_total_favoritos_artista(artista_id)
        
        return {
            'total_obras': total_obras,
            'obras_visibles': obras_visibles,
            'obras_ocultas': total_obras - obras_visibles,
            'total_favoritos': total_favoritos
        }
        
    def get_artistas_con_obras(self, limit=None):
        """
        Obtener artistas que tienen obras publicadas
        """
        return self.obra_repo.get_artistas_con_obras(limit=limit)
