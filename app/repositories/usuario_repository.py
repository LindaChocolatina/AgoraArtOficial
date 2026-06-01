from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base_repository import BaseRepository
from app.models.usuario import Usuario

class UsuarioRepository(BaseRepository):
    """
    Repositorio específico para usuarios
    Extiende BaseRepository con operaciones personalizadas
    """
    
    def __init__(self, session):
        """Inicializar repositorio de usuarios"""
        super().__init__(Usuario, session)
    
    def get_by_email(self, email):
        """
        Obtener usuario por email
        
        Args:
            email (str): Email del usuario
            
        Returns:
            Usuario: Instancia del usuario o None
        """
        try:
            return self.session.query(Usuario).filter_by(email=email).first()
        except SQLAlchemyError as e:
            print(f"Error al obtener usuario por email: {e}")
            return None
    
    def get_by_username(self, username):
        """
        Obtener usuario por username
        
        Args:
            username (str): Username del usuario
            
        Returns:
            Usuario: Instancia del usuario o None
        """
        try:
            return self.session.query(Usuario).filter_by(username=username).first()
        except SQLAlchemyError as e:
            print(f"Error al obtener usuario por username: {e}")
            return None
    
    def email_exists(self, email, exclude_id=None):
        """
        Verificar si email ya existe
        
        Args:
            email (str): Email a verificar
            exclude_id (int): ID a excluir de la verificación
            
        Returns:
            bool: True si existe, False si no
        """
        try:
            query = self.session.query(Usuario).filter_by(email=email)
            if exclude_id:
                query = query.filter(Usuario.id_usuario != exclude_id)
            return query.first() is not None
        except SQLAlchemyError as e:
            print(f"Error al verificar existencia de email: {e}")
            return False
    
    def username_exists(self, username, exclude_id=None):
        """
        Verificar si username ya existe
        
        Args:
            username (str): Username a verificar
            exclude_id (int): ID a excluir de la verificación
            
        Returns:
            bool: True si existe, False si no
        """
        try:
            query = self.session.query(Usuario).filter_by(username=username)
            if exclude_id:
                query = query.filter(Usuario.id_usuario != exclude_id)
            return query.first() is not None
        except SQLAlchemyError as e:
            print(f"Error al verificar existencia de username: {e}")
            return False
    
    def get_by_rol(self, rol, limit=None, offset=None):
        """
        Obtener usuarios por rol
        
        Args:
            rol (str): Rol a filtrar ('admin', 'artista', 'cliente')
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de usuarios con el rol especificado
        """
        try:
            query = self.session.query(Usuario).filter_by(rol=rol, estado='activo')
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener usuarios por rol: {e}")
            return []
    
    def get_artistas_activos(self, limit=None, offset=None):
        """
        Obtener artistas activos
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de artistas activos
        """
        return self.get_by_rol('artista', limit, offset)
    
    def get_clientes_activos(self, limit=None, offset=None):
        """
        Obtener clientes activos
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de clientes activos
        """
        return self.get_by_rol('cliente', limit, offset)
    
    def buscar_usuarios(self, termino, rol=None, limit=None):
        """
        Buscar usuarios por nombre o username
        
        Args:
            termino (str): Término de búsqueda
            rol (str): Rol opcional a filtrar
            limit (int): Límite de resultados
            
        Returns:
            list: Lista de usuarios que coinciden con la búsqueda
        """
        try:
            query = self.session.query(Usuario).filter(
                Usuario.estado == 'activo',
                (Usuario.nombre.contains(termino) | Usuario.username.contains(termino))
            )
            
            if rol:
                query = query.filter_by(rol=rol)
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al buscar usuarios: {e}")
            return []

    def get_artistas_por_categoria(self, categoria_id, termino=None, limit=None, offset=None):
        """
        Obtener artistas activos con obras visibles en una categoría.

        Args:
            categoria_id (int): ID de la categoría
            termino (str): Filtro opcional por nombre o username
            limit (int): Límite de resultados
            offset (int): Desplazamiento

        Returns:
            list: Lista de artistas
        """
        try:
            from app.models.obra import Obra

            artistas_ids = self.session.query(Obra.id_artista).filter(
                Obra.id_categoria == categoria_id,
                Obra.visible == True
            ).distinct()

            query = self.session.query(Usuario).filter(
                Usuario.estado == 'activo',
                Usuario.rol == 'artista',
                Usuario.id_usuario.in_(artistas_ids)
            )

            if termino:
                query = query.filter(
                    Usuario.nombre.contains(termino) | Usuario.username.contains(termino)
                )

            query = query.order_by(Usuario.nombre)

            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)

            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener artistas por categoría: {e}")
            return []
    
    def toggle_estado(self, usuario_id, usuario_admin_id=None):
        """
        Cambiar estado de usuario (activo/bloqueado)
        
        Args:
            usuario_id (int): ID del usuario a modificar
            usuario_admin_id (int): ID del administrador que realiza la acción
            
        Returns:
            Usuario: Usuario actualizado o None si hay error
        """
        try:
            usuario = self.get_by_id(usuario_id)
            if usuario:
                nuevo_estado = 'bloqueado' if usuario.estado == 'activo' else 'activo'
                return self.update(usuario_id, {'estado': nuevo_estado}, usuario_admin_id)
            return None
        except SQLAlchemyError as e:
            print(f"Error al cambiar estado de usuario: {e}")
            return None
    
    def get_seguidores(self, artista_id, limit=None, offset=None):
        """
        Obtener seguidores de un artista
        
        Args:
            artista_id (int): ID del artista
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de usuarios que siguen al artista
        """
        try:
            from app.models.usuario import favoritos_artistas, Usuario
            
            query = self.session.query(Usuario).join(
                favoritos_artistas, Usuario.id_usuario == favoritos_artistas.c.id_usuario
            ).filter(
                favoritos_artistas.c.id_artista == artista_id
            ).order_by(favoritos_artistas.c.fecha_seguimiento.desc())
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
                
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener seguidores: {e}")
            return []
    
    def get_siguiendo(self, usuario_id, limit=None, offset=None):
        """
        Obtener artistas que sigue un usuario
        
        Args:
            usuario_id (int): ID del usuario
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de artistas que sigue el usuario
        """
        try:
            from app.models.usuario import favoritos_artistas, Usuario
            
            query = self.session.query(Usuario).join(
                favoritos_artistas, Usuario.id_usuario == favoritos_artistas.c.id_artista
            ).filter(
                favoritos_artistas.c.id_usuario == usuario_id
            ).order_by(favoritos_artistas.c.fecha_seguimiento.desc())
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
                
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener artistas seguidos: {e}")
            return []
    
    def seguir_artista(self, usuario_id, artista_id):
        """
        Hacer que un usuario siga a un artista
        
        Args:
            usuario_id (int): ID del usuario
            artista_id (int): ID del artista
            
        Returns:
            bool: True si se siguió correctamente, False si ya seguía o hay error
        """
        try:
            from app.models.usuario import favoritos_artistas
            
            # Verificar si ya sigue al artista
            existe = self.session.query(favoritos_artistas).filter_by(
                id_usuario=usuario_id, id_artista=artista_id
            ).first()
            
            if existe:
                return True
            
            # Agregar relación
            self.session.execute(
                favoritos_artistas.insert().values(
                    id_usuario=usuario_id,
                    id_artista=artista_id
                )
            )
            
            return True
        except SQLAlchemyError as e:
            print(f"Error al seguir artista: {e}")
            return False
    
    def dejar_de_seguir_artista(self, usuario_id, artista_id):
        """
        Hacer que un usuario deje de seguir a un artista
        
        Args:
            usuario_id (int): ID del usuario
            artista_id (int): ID del artista
            
        Returns:
            bool: True si se dejó de seguir correctamente, False si no seguía o hay error
        """
        try:
            from app.models.usuario import favoritos_artistas
            
            # Eliminar relación
            result = self.session.execute(
                favoritos_artistas.delete().where(
                    favoritos_artistas.c.id_usuario == usuario_id,
                    favoritos_artistas.c.id_artista == artista_id
                )
            )
            
            return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Error al dejar de seguir artista: {e}")
            return False
    
    def esta_siguiendo_artista(self, usuario_id, artista_id):
        """
        Verificar si un usuario sigue a un artista
        
        Args:
            usuario_id (int): ID del usuario
            artista_id (int): ID del artista
            
        Returns:
            bool: True si sigue al artista
        """
        try:
            from app.models.usuario import favoritos_artistas
            
            existe = self.session.query(favoritos_artistas).filter_by(
                id_usuario=usuario_id, id_artista=artista_id
            ).first()
            
            return existe is not None
        except SQLAlchemyError as e:
            print(f"Error al verificar seguimiento: {e}")
            return False
    
    def get_siguiendo_count(self, usuario_id):
        """
        Obtener cantidad de artistas que sigue un usuario
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            int: Cantidad de artistas seguidos
        """
        try:
            from app.models.usuario import favoritos_artistas
            
            return self.session.query(favoritos_artistas).filter_by(
                id_usuario=usuario_id
            ).count()
        except SQLAlchemyError as e:
            print(f"Error al contar artistas seguidos: {e}")
            return 0
    
    def get_seguidores_count(self, artista_id):
        """
        Obtener cantidad de seguidores de un artista
        
        Args:
            artista_id (int): ID del artista
            
        Returns:
            int: Cantidad de seguidores
        """
        try:
            from app.models.usuario import favoritos_artistas
            
            return self.session.query(favoritos_artistas).filter_by(
                id_artista=artista_id
            ).count()
        except SQLAlchemyError as e:
            print(f"Error al contar seguidores: {e}")
            return 0

