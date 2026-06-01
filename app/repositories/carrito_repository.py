from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

from app.models.ecommerce import CarritoItem


class CarritoRepository:
    """Repositorio del carrito persistente por usuario."""

    def __init__(self, session):
        self.session = session

    def get_items_by_usuario(self, usuario_id):
        try:
            return (
                self.session.query(CarritoItem)
                .filter_by(id_usuario=usuario_id)
                .order_by(CarritoItem.fecha_actualizacion.desc())
                .all()
            )
        except SQLAlchemyError as e:
            print(f'Error al obtener carrito del usuario: {e}')
            return []

    def get_item(self, usuario_id, producto_id):
        try:
            return (
                self.session.query(CarritoItem)
                .filter_by(id_usuario=usuario_id, id_producto=producto_id)
                .first()
            )
        except SQLAlchemyError as e:
            print(f'Error al obtener item del carrito: {e}')
            return None

    def add_or_increment(self, usuario_id, producto_id, cantidad=1):
        try:
            item = self.get_item(usuario_id, producto_id)
            if item:
                item.cantidad += cantidad
                item.fecha_actualizacion = datetime.utcnow()
            else:
                item = CarritoItem(
                    id_usuario=usuario_id,
                    id_producto=producto_id,
                    cantidad=cantidad,
                )
                self.session.add(item)
            self.session.flush()
            return item
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f'Error al agregar al carrito: {e}')
            return None

    def set_cantidad(self, usuario_id, producto_id, cantidad):
        try:
            item = self.get_item(usuario_id, producto_id)
            if not item:
                return None
            item.cantidad = cantidad
            item.fecha_actualizacion = datetime.utcnow()
            self.session.flush()
            return item
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f'Error al actualizar cantidad del carrito: {e}')
            return None

    def remove_item(self, usuario_id, producto_id):
        try:
            item = self.get_item(usuario_id, producto_id)
            if not item:
                return False
            self.session.delete(item)
            self.session.flush()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f'Error al quitar item del carrito: {e}')
            return False

    def clear_usuario(self, usuario_id):
        try:
            self.session.query(CarritoItem).filter_by(id_usuario=usuario_id).delete()
            self.session.flush()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f'Error al vaciar carrito: {e}')
            return False

    def get_total_count(self, usuario_id):
        try:
            total = (
                self.session.query(func.coalesce(func.sum(CarritoItem.cantidad), 0))
                .filter_by(id_usuario=usuario_id)
                .scalar()
            )
            return int(total or 0)
        except SQLAlchemyError as e:
            print(f'Error al contar items del carrito: {e}')
            return 0

    def save(self):
        try:
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            print(f'Error al guardar carrito: {e}')
            return False
