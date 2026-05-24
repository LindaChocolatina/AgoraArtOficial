from sqlalchemy.exc import SQLAlchemyError
from app.repositories.base_repository import BaseRepository
from app.models.ecommerce import Direccion

class DireccionRepository(BaseRepository):
    """
    Repositorio específico para Direcciones de envío
    """
    
    def __init__(self, session):
        """Inicializar repositorio de direcciones"""
        super().__init__(Direccion, session)
    
    def get_by_usuario(self, usuario_id):
        """Obtener todas las direcciones de un usuario"""
        try:
            return self.session.query(Direccion).filter_by(id_usuario=usuario_id).order_by(Direccion.fecha_creacion.desc()).all()
        except SQLAlchemyError as e:
            print(f"Error al obtener direcciones del usuario: {e}")
            return []

    def get_by_id_and_usuario(self, id_direccion, usuario_id):
        """Obtener una dirección solo si pertenece al usuario"""
        try:
            return self.session.query(Direccion).filter_by(
                id_direccion=id_direccion,
                id_usuario=usuario_id
            ).first()
        except SQLAlchemyError as e:
            print(f"Error al obtener dirección del usuario: {e}")
            return None

    def delete(self, id_value, usuario_id=None, registrar_auditoria=True):
        """Eliminar solo si no tiene órdenes asociadas"""
        try:
            direccion = self.get_by_id(id_value)
            if not direccion:
                return False
            if direccion.tiene_ordenes_asociadas():
                return False
            return super().delete(id_value, usuario_id=usuario_id, registrar_auditoria=registrar_auditoria)
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f"Error al eliminar dirección: {e}")
            return False
    
    def set_default(self, usuario_id, id_direccion):
        """
        Establecer una dirección como predeterminada (si tuviéramos ese campo)
        Por ahora solo es un stub para futura funcionalidad.
        """
        pass
