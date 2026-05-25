"""
Servicio de gestión de usuarios
Maneja operaciones de negocio relacionadas con usuarios
"""

class UsuarioService:
    """
    Servicio de usuarios para operaciones de negocio
    """
    
    def __init__(self, usuario_repository):
        """
        Inicializar servicio de usuarios
        
        Args:
            usuario_repository: Repositorio de usuarios
        """
        self.usuario_repo = usuario_repository
    
    def get_by_id(self, usuario_id):
        """
        Obtener usuario por ID
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            Usuario: Instancia del usuario o None
        """
        return self.usuario_repo.get_by_id(usuario_id)
    
    def get_by_email(self, email):
        """
        Obtener usuario por email
        
        Args:
            email (str): Email del usuario
            
        Returns:
            Usuario: Instancia del usuario o None
        """
        return self.usuario_repo.get_by_email(email)
    
    def get_all(self, filters=None, limit=None, offset=None):
        """
        Obtener todos los usuarios con filtros opcionales
        
        Args:
            filters (dict): Filtros a aplicar
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de usuarios
        """
        return self.usuario_repo.get_all(filters=filters, limit=limit, offset=offset)
    
    def buscar_usuarios(self, termino, rol=None, limit=None):
        """
        Buscar usuarios por término
        
        Args:
            termino (str): Término de búsqueda
            rol (str): Filtrar por rol
            limit (int): Límite de resultados
            
        Returns:
            list: Lista de usuarios que coinciden
        """
        return self.usuario_repo.buscar_usuarios(termino, rol=rol, limit=limit)
    
    def actualizar_usuario(self, usuario_id, data, usuario_modificador=None):
        """
        Actualizar datos de usuario
        
        Args:
            usuario_id (int): ID del usuario
            data (dict): Datos a actualizar
            usuario_modificador (int): ID del usuario que modifica
            
        Returns:
            tuple: (bool, Usuario) - (exitoso, usuario_actualizado)
        """
        # Validar datos básicos
        if 'email' in data:
            if '@' not in data['email'] or '.' not in data['email']:
                return (False, None)
        
        if 'username' in data:
            if len(data['username']) < 3:
                return (False, None)
        
        # Actualizar usuario
        usuario_actualizado = self.usuario_repo.update(usuario_id, data, usuario_modificador)
        
        if usuario_actualizado:
            self.usuario_repo.save()
            return (True, usuario_actualizado)
        
        return (False, None)
    
    def toggle_estado(self, usuario_id, usuario_modificador=None):
        """
        Cambiar estado de usuario (activo/bloqueado)
        
        Args:
            usuario_id (int): ID del usuario
            usuario_modificador (int): ID del usuario que modifica
            
        Returns:
            Usuario: Usuario actualizado o None
        """
        usuario = self.usuario_repo.get_by_id(usuario_id)
        if not usuario:
            return None
        
        nuevo_estado = 'bloqueado' if usuario.estado == 'activo' else 'activo'
        
        return self.usuario_repo.update(usuario_id, {'estado': nuevo_estado}, usuario_modificador)
    
    def get_artistas_activos(self, limit=None, offset=None):
        """
        Obtener artistas activos
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de artistas activos
        """
        return self.usuario_repo.get_artistas_activos(limit=limit, offset=offset)
    
    def seguir_artista(self, usuario_id, artista_id):
        """
        Seguir a un artista
        
        Args:
            usuario_id (int): ID del cliente que sigue
            artista_id (int): ID del artista a seguir
            
        Returns:
            bool: True si se siguió correctamente
        """
        if self.usuario_repo.esta_siguiendo_artista(usuario_id, artista_id):
            return True
        ok = self.usuario_repo.seguir_artista(usuario_id, artista_id)
        if ok:
            from app.factories.app_factory import db
            db.session.commit()
        return ok
    
    def dejar_de_seguir_artista(self, usuario_id, artista_id):
        """
        Dejar de seguir a un artista
        
        Args:
            usuario_id (int): ID del cliente
            artista_id (int): ID del artista
            
        Returns:
            bool: True si se dejó de seguir correctamente
        """
        ok = self.usuario_repo.dejar_de_seguir_artista(usuario_id, artista_id)
        if ok:
            from app.factories.app_factory import db
            db.session.commit()
        return ok
    
    def esta_siguiendo_artista(self, usuario_id, artista_id):
        """
        Verificar si un usuario sigue a un artista
        
        Args:
            usuario_id (int): ID del usuario
            artista_id (int): ID del artista
            
        Returns:
            bool: True si sigue al artista
        """
        return self.usuario_repo.esta_siguiendo_artista(usuario_id, artista_id)
    
    def get_siguiendo(self, usuario_id, limit=None, offset=None):
        """
        Obtener artistas que sigue un usuario
        
        Args:
            usuario_id (int): ID del usuario
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de artistas seguidos
        """
        return self.usuario_repo.get_siguiendo(usuario_id, limit=limit, offset=offset)
    
    def get_seguidores(self, artista_id, limit=None, offset=None):
        """
        Obtener seguidores de un artista
        
        Args:
            artista_id (int): ID del artista
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de seguidores
        """
        return self.usuario_repo.get_seguidores(artista_id, limit=limit, offset=offset)
    
    def get_siguiendo_count(self, usuario_id):
        """
        Obtener cantidad de artistas que sigue un usuario
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            int: Cantidad de artistas seguidos
        """
        return self.usuario_repo.get_siguiendo_count(usuario_id)
    
    def get_seguidores_count(self, artista_id):
        """
        Obtener cantidad de seguidores de un artista
        
        Args:
            artista_id (int): ID del artista
            
        Returns:
            int: Cantidad de seguidores
        """
        return self.usuario_repo.get_seguidores_count(artista_id)
    
    def count(self, filters=None):
        """
        Contar usuarios con filtros opcionales
        
        Args:
            filters (dict): Filtros a aplicar
            
        Returns:
            int: Cantidad de usuarios
        """
        return self.usuario_repo.count(filters=filters)
    
    def delete_usuario(self, usuario_id, usuario_modificador=None):
        """
        Eliminar usuario (soft delete)
        
        Args:
            usuario_id (int): ID del usuario
            usuario_modificador (int): ID del usuario que elimina
            
        Returns:
            bool: True si se eliminó correctamente
        """
        # En lugar de eliminar físicamente, lo bloqueamos
        return self.usuario_repo.update(usuario_id, {'estado': 'bloqueado'}, usuario_modificador) is not None
