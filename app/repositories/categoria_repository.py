from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from app.repositories.base_repository import BaseRepository
from app.models.categoria import Categoria
from app.models.obra import Obra

class CategoriaRepository(BaseRepository):
    """
    Repositorio específico para categorías
    Extiende BaseRepository con operaciones personalizadas
    """
    
    def __init__(self, session):
        """Inicializar repositorio de categorías"""
        super().__init__(Categoria, session)

    def get_all(self, filters=None, order_by=None, limit=None, offset=None):
        if order_by is None:
            order_by = 'nombre'
        return super().get_all(filters=filters, order_by=order_by, limit=limit, offset=offset)
    
    def get_all_with_obras_count(self):
        """
        Obtener todas las categorías con conteo de obras
        
        Returns:
            list: Lista de tuplas (Categoria, obras_count)
        """
        try:
            result = self.session.query(
                Categoria,
                func.count(Obra.id_obra).label('obras_count')
            ).outerjoin(
                Obra, 
                (Categoria.id_categoria == Obra.id_categoria) & (Obra.visible == True)
            ).group_by(Categoria.id_categoria).order_by(Categoria.nombre).all()
            
            return result
        except SQLAlchemyError as e:
            print(f"Error al obtener categorías con conteo: {e}")
            return []
    
    def get_by_name(self, nombre):
        """
        Obtener categoría por nombre
        
        Args:
            nombre (str): Nombre de la categoría
            
        Returns:
            Categoria: Instancia de la categoría o None
        """
        try:
            return self.session.query(Categoria).filter_by(nombre=nombre).first()
        except SQLAlchemyError as e:
            print(f"Error al obtener categoría por nombre: {e}")
            return None
    
    def name_exists(self, nombre, exclude_id=None):
        """
        Verificar si nombre de categoría ya existe
        
        Args:
            nombre (str): Nombre a verificar
            exclude_id (int): ID a excluir de la verificación
            
        Returns:
            bool: True si existe, False si no
        """
        try:
            query = self.session.query(Categoria).filter_by(nombre=nombre)
            if exclude_id:
                query = query.filter(Categoria.id_categoria != exclude_id)
            return query.first() is not None
        except SQLAlchemyError as e:
            print(f"Error al verificar existencia de nombre de categoría: {e}")
            return False
    
    def get_with_obras(self, categoria_id, limit=None, offset=None):
        """
        Obtener categoría con sus obras
        
        Args:
            categoria_id (int): ID de la categoría
            limit (int): Límite de obras
            offset (int): Desplazamiento de obras
            
        Returns:
            tuple: (Categoria, obras_list)
        """
        try:
            categoria = self.get_by_id(categoria_id)
            if not categoria:
                return (None, [])
            
            query = self.session.query(Obra).filter_by(
                id_categoria=categoria_id, 
                visible=True
            ).order_by(Obra.fecha_publicacion.desc())
            
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            obras = query.all()
            return (categoria, obras)
        except SQLAlchemyError as e:
            print(f"Error al obtener categoría con obras: {e}")
            return (None, [])
    
    def get_populares(self, limit=None):
        """
        Obtener categorías más populares (con más obras)
        
        Args:
            limit (int): Límite de resultados
            
        Returns:
            list: Lista de tuplas (Categoria, obras_count)
        """
        try:
            result = self.session.query(
                Categoria,
                func.count(Obra.id_obra).label('obras_count')
            ).join(
                Obra, 
                (Categoria.id_categoria == Obra.id_categoria) & (Obra.visible == True)
            ).group_by(Categoria.id_categoria).order_by(
                func.count(Obra.id_obra).desc()
            )
            
            if limit:
                result = result.limit(limit)
            
            return result.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener categorías populares: {e}")
            return []
    
    def get_empty_categories(self):
        """
        Obtener categorías sin obras
        
        Returns:
            list: Lista de categorías sin obras
        """
        try:
            subquery = self.session.query(Obra.id_categoria).filter(
                Obra.visible == True
            ).distinct().subquery()
            
            result = self.session.query(Categoria).filter(
                ~Categoria.id_categoria.in_(subquery)
            ).order_by(Categoria.nombre).all()
            
            return result
        except SQLAlchemyError as e:
            print(f"Error al obtener categorías vacías: {e}")
            return []
    
    def buscar_categorias(self, termino, limit=None):
        """
        Buscar categorías por nombre o descripción
        
        Args:
            termino (str): Término de búsqueda
            limit (int): Límite de resultados
            
        Returns:
            list: Lista de categorías que coinciden con la búsqueda
        """
        try:
            query = self.session.query(Categoria).filter(
                (Categoria.nombre.contains(termino) | 
                 Categoria.descripcion.contains(termino))
            ).order_by(Categoria.nombre)
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        except SQLAlchemyError as e:
            print(f"Error al buscar categorías: {e}")
            return []
    
    def get_obras_count(self, categoria_id):
        """
        Obtener cantidad de obras en una categoría
        
        Args:
            categoria_id (int): ID de la categoría
            
        Returns:
            int: Cantidad de obras
        """
        try:
            return self.session.query(Obra).filter_by(
                id_categoria=categoria_id, 
                visible=True
            ).count()
        except SQLAlchemyError as e:
            print(f"Error al contar obras de categoría: {e}")
            return 0
    
    def get_artistas_count(self, categoria_id):
        """
        Obtener cantidad de artistas únicos en una categoría
        
        Args:
            categoria_id (int): ID de la categoría
            
        Returns:
            int: Cantidad de artistas únicos
        """
        try:
            from app.models.usuario import Usuario
            
            result = self.session.query(
                func.count(func.distinct(Obra.id_artista))
            ).filter_by(
                id_categoria=categoria_id, 
                visible=True
            ).scalar()
            
            return result or 0
        except SQLAlchemyError as e:
            print(f"Error al contar artistas de categoría: {e}")
            return 0
    
    def update_with_obras_count(self, categoria_id, data, usuario_id=None):
        """
        Actualizar categoría y registrar cambios en obras
        
        Args:
            categoria_id (int): ID de la categoría
            data (dict): Datos a actualizar
            usuario_id (int): ID del usuario que realiza la acción
            
        Returns:
            Categoria: Categoría actualizada o None si hay error
        """
        try:
            # Obtener cantidad de obras antes de actualizar
            obras_count = self.get_obras_count(categoria_id)
            
            # Actualizar categoría
            categoria = self.update(categoria_id, data, usuario_id)
            
            if categoria:
                # Si se cambió el nombre, registrar qué obras se afectaron
                if 'nombre' in data:
                    descripcion = f"Categoría actualizada: {obras_count} obras afectadas"
                    # Actualizar descripción en auditoría
                    from app.models.auditoria import Auditoria
                    ultima_auditoria = self.session.query(Auditoria).filter_by(
                        tabla_afectada='categorias',
                        id_registro=categoria_id
                    ).order_by(Auditoria.fecha.desc()).first()
                    
                    if ultima_auditoria:
                        ultima_auditoria.descripcion = descripcion
            
            return categoria
        except SQLAlchemyError as e:
            print(f"Error al actualizar categoría con conteo: {e}")
            return None
            
    def get_populares(self, limit=None):
        """
        Obtener categorías populares (con más obras)
        """
        try:
            result = self.session.query(
                Categoria,
                func.count(Obra.id_obra).label('obras_count')
            ).join(
                Obra, 
                Categoria.id_categoria == Obra.id_categoria
            ).filter(Obra.visible == True).group_by(Categoria.id_categoria).order_by(func.count(Obra.id_obra).desc())
            
            if limit:
                result = result.limit(limit)
                
            return result.all()
        except SQLAlchemyError as e:
            print(f"Error al obtener categorías populares: {e}")
            return []
