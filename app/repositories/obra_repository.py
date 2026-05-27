from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from app.repositories.base_repository import BaseRepository
from app.models.obra import Obra
from app.models.usuario import favoritos_obras

class ObraRepository(BaseRepository):
    """
    Repositorio específico para obras
    Extiende BaseRepository con operaciones personalizadas
    """
    
    def __init__(self, session):
        """Inicializar repositorio de obras"""
        super().__init__(Obra, session)
    
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
        try:
            query = self.session.query(Obra).filter_by(id_artista=artista_id)
            
            if visible_only:
                query = query.filter_by(visible=True)
            
            query = query.order_by(Obra.fecha_publicacion.desc())
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener obras del artista: {e}")
            return []
    
    def get_by_categoria(self, categoria_id, visible_only=True, limit=None, offset=None):
        """
        Obtener obras por categoría
        
        Args:
            categoria_id (int): ID de la categoría
            visible_only (bool): Solo obras visibles
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de obras de la categoría
        """
        try:
            query = self.session.query(Obra).filter_by(id_categoria=categoria_id)
            
            if visible_only:
                query = query.filter_by(visible=True)
            
            query = query.order_by(Obra.fecha_publicacion.desc())
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener obras por categoría: {e}")
            return []
    
    def get_publicas(self, limit=None, offset=None, categoria_id=None, artista_id=None):
        """
        Obtener obras públicas con filtros opcionales
        
        Args:
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            categoria_id (int): Filtro por categoría
            artista_id (int): Filtro por artista
            
        Returns:
            list: Lista de obras públicas
        """
        try:
            query = self.session.query(Obra).filter_by(visible=True)
            
            if categoria_id:
                query = query.filter_by(id_categoria=categoria_id)
            
            if artista_id:
                query = query.filter_by(id_artista=artista_id)
            
            query = query.order_by(Obra.fecha_publicacion.desc())
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener obras públicas: {e}")
            return []
    
    def buscar_obras(self, termino, limit=None, offset=None):
        """
        Buscar obras por título o descripción
        
        Args:
            termino (str): Término de búsqueda
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de obras que coinciden con la búsqueda
        """
        try:
            query = self.session.query(Obra).filter(
                Obra.visible == True,
                or_(
                    Obra.titulo.contains(termino),
                    Obra.descripcion.contains(termino),
                    Obra.tecnica.contains(termino)
                )
            ).order_by(Obra.fecha_publicacion.desc())
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al buscar obras: {e}")
            return []
    
    def toggle_visibilidad(self, obra_id, usuario_id=None):
        """
        Cambiar visibilidad de una obra
        
        Args:
            obra_id (int): ID de la obra
            usuario_id (int): ID del usuario que realiza la acción
            
        Returns:
            Obra: Obra actualizada o None si hay error
        """
        try:
            obra = self.get_by_id(obra_id)
            if obra:
                nuevo_estado = not obra.visible
                return self.update(obra_id, {'visible': nuevo_estado}, usuario_id)
            return None
        except SQLAlchemyError as e:
            print(f"Error al cambiar visibilidad de obra: {e}")
            return None
    
    def agregar_favorito(self, usuario_id, obra_id):
        """
        Agregar obra a favoritos de usuario
        
        Args:
            usuario_id (int): ID del usuario
            obra_id (int): ID de la obra
            
        Returns:
            bool: True si se agregó correctamente, False si ya era favorito o hay error
        """
        try:
            # Verificar si ya es favorito
            existe = self.session.query(favoritos_obras).filter_by(
                id_usuario=usuario_id, id_obra=obra_id
            ).first()
            
            if existe:
                return True
            
            # Agregar a favoritos
            self.session.execute(
                favoritos_obras.insert().values(
                    id_usuario=usuario_id,
                    id_obra=obra_id
                )
            )
            
            return True
        except SQLAlchemyError as e:
            print(f"Error al agregar obra a favoritos: {e}")
            return False
    
    def quitar_favorito(self, usuario_id, obra_id):
        """
        Quitar obra de favoritos de usuario
        
        Args:
            usuario_id (int): ID del usuario
            obra_id (int): ID de la obra
            
        Returns:
            bool: True si se quitó correctamente, False si no era favorito o hay error
        """
        try:
            result = self.session.execute(
                favoritos_obras.delete().where(
                    favoritos_obras.c.id_usuario == usuario_id,
                    favoritos_obras.c.id_obra == obra_id
                )
            )
            
            return result.rowcount > 0
        except SQLAlchemyError as e:
            print(f"Error al quitar obra de favoritos: {e}")
            return False
    
    def es_favorito(self, usuario_id, obra_id):
        """
        Verificar si una obra es favorita de un usuario
        
        Args:
            usuario_id (int): ID del usuario
            obra_id (int): ID de la obra
            
        Returns:
            bool: True si es favorito, False si no
        """
        try:
            existe = self.session.query(favoritos_obras).filter_by(
                id_usuario=usuario_id, id_obra=obra_id
            ).first()
            
            return existe is not None
        except SQLAlchemyError as e:
            print(f"Error al verificar si obra es favorita: {e}")
            return False
    
    def get_favoritos_usuario(self, usuario_id, limit=None, offset=None):
        """
        Obtener obras favoritas de un usuario
        
        Args:
            usuario_id (int): ID del usuario
            limit (int): Límite de resultados
            offset (int): Desplazamiento
            
        Returns:
            list: Lista de obras favoritas del usuario
        """
        try:
            query = self.session.query(Obra).join(
                favoritos_obras, Obra.id_obra == favoritos_obras.c.id_obra
            ).filter(
                favoritos_obras.c.id_usuario == usuario_id,
                Obra.visible == True
            ).order_by(favoritos_obras.c.fecha_agregado.desc())
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener obras favoritas: {e}")
            return []
    
    def get_obras_recientes(self, dias=30, limit=None):
        """
        Obtener obras publicadas recientemente
        
        Args:
            dias (int): Días hacia atrás
            limit (int): Límite de resultados
            
        Returns:
            list: Lista de obras recientes
        """
        try:
            from datetime import datetime, timedelta
            
            fecha_limite = datetime.utcnow() - timedelta(days=dias)
            
            query = self.session.query(Obra).filter(
                Obra.visible == True,
                Obra.fecha_publicacion >= fecha_limite
            ).order_by(Obra.fecha_publicacion.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener obras recientes: {e}")
            return []
    
    def get_artistas_con_obras(self, limit=None):
        """
        Obtener artistas que tienen obras
        
        Args:
            limit (int): Límite de resultados
            
        Returns:
            list: Lista de artistas con obras
        """
        try:
            query = self.session.query(Obra.id_artista).distinct()
            
            if limit:
                query = query.limit(limit)
            
            artistas_ids = [row[0] for row in query.all()]
            
            # Obtener los objetos Usuario completos
            from app.models.usuario import Usuario
            artistas = self.session.query(Usuario).filter(
                Usuario.id_usuario.in_(artistas_ids)
            ).all()
            
            return artistas
        except SQLAlchemyError as e:
            print(f"Error al obtener artistas con obras: {e}")
            return []
    
    def get_count_by_artista(self, artista_id, visible_only=True):
        """
        Obtener cantidad de obras de un artista
        
        Args:
            artista_id (int): ID del artista
            visible_only (bool): Solo obras visibles
            
        Returns:
            int: Cantidad de obras
        """
        try:
            query = self.session.query(Obra).filter_by(id_artista=artista_id)
            
            if visible_only:
                query = query.filter_by(visible=True)
            
            return query.count()
        except SQLAlchemyError as e:
            print(f"Error al contar obras del artista: {e}")
            return 0

    def get_favoritos_count(self, usuario_id):
        """
        Obtener cantidad de obras favoritas de un usuario
        
        Args:
            usuario_id (int): ID del usuario
            
        Returns:
            int: Cantidad de obras favoritas
        """
        try:
            return self.session.query(favoritos_obras).filter_by(
                id_usuario=usuario_id
            ).count()
        except SQLAlchemyError as e:
            print(f"Error al contar obras favoritas: {e}")
            return 0
