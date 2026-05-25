from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base_repository import BaseRepository
from app.models.moodboard import Lienzo, LienzoItem

class MoodboardRepository(BaseRepository):
    """
    Repositorio específico para Moodboards (Lienzos)
    """
    
    def __init__(self, session):
        """Inicializar repositorio de moodboards"""
        super().__init__(Lienzo, session)
    
    def get_by_usuario(self, usuario_id):
        """Obtener todos los lienzos de un usuario"""
        try:
            return self.session.query(Lienzo).filter_by(id_usuario=usuario_id).order_by(Lienzo.fecha_creacion.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error al obtener lienzos del usuario: {e}")
            return []
    
    def get_items(self, id_lienzo):
        """Obtener obras guardadas en un lienzo (lista materializada)."""
        try:
            return (
                self.session.query(LienzoItem)
                .filter_by(id_lienzo=id_lienzo)
                .all()
            )
        except SQLAlchemyError as e:
            print(f"Error al obtener items del lienzo: {e}")
            return []

    def get_item(self, id_lienzo, id_obra):
        """Obtener un item específico de un lienzo"""
        try:
            return self.session.query(LienzoItem).filter_by(id_lienzo=id_lienzo, id_obra=id_obra).first()
        except SQLAlchemyError as e:
            print(f"Error al obtener item del lienzo: {e}")
            return None
    
    def agregar_item(self, id_lienzo, id_obra, nota=None):
        """Agregar una obra a un lienzo"""
        try:
            item = LienzoItem(id_lienzo=id_lienzo, id_obra=id_obra, nota=nota)
            self.session.add(item)
            return True
        except SQLAlchemyError as e:
            print(f"Error al agregar obra al lienzo: {e}")
            return False
    
    def remover_item(self, id_lienzo, id_obra):
        """Remover una obra de un lienzo"""
        try:
            item = self.get_item(id_lienzo, id_obra)
            if item:
                self.session.delete(item)
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Error al remover obra del lienzo: {e}")
            return False
