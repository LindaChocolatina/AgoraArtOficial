from app.models.ecommerce import Orden, OrdenItem, Pago
from sqlalchemy import desc
import logging


class OrdenService:
    def __init__(self, session=None):
        self.session = session

    def crear_orden_pendiente(self, cliente_id, direccion_id, total, items):
        """
        Reserva la orden sin descontar stock (espera confirmación de pago).
        """
        try:
            nueva_orden = Orden(
                id_cliente=cliente_id,
                id_direccion=direccion_id,
                total=total,
                estado='pendiente',
            )
            self.session.add(nueva_orden)
            self.session.flush()

            for item in items:
                producto = item['producto']
                cantidad = item['cantidad']
                orden_item = OrdenItem(
                    id_orden=nueva_orden.id_orden,
                    id_producto=producto.id_producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=float(producto.precio) * cantidad,
                )
                self.session.add(orden_item)

            self.session.commit()
            return True, nueva_orden
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error al crear orden pendiente: {e}")
            return False, None

    def confirmar_pago(self, orden_id, proveedor, referencia, monto):
        """
        Marca la orden como pagada, descuenta stock y registra el pago.
        """
        from app.factories.service_factory import get_service_factory

        try:
            orden = self.session.query(Orden).filter_by(id_orden=orden_id).first()
            if not orden:
                return False, 'Orden no encontrada'
            if orden.estado == 'pagada':
                return True, orden
            if orden.estado != 'pendiente':
                return False, 'La orden ya no puede pagarse'

            producto_service = get_service_factory(self.session).get_producto_service()

            for item in orden.items.all():
                if not producto_service.verificar_disponibilidad(item.id_producto, item.cantidad):
                    self.session.rollback()
                    return False, 'Uno o más productos ya no tienen stock suficiente'
                if not producto_service.reducir_stock_venta(item.id_producto, item.cantidad):
                    self.session.rollback()
                    return False, 'No se pudo actualizar el inventario'

            pago = Pago(
                id_orden=orden.id_orden,
                proveedor=proveedor,
                referencia=referencia,
                estado='aprobado',
                monto=monto or orden.total,
            )
            orden.estado = 'pagada'
            self.session.add(pago)
            self.session.commit()
            return True, orden
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error al confirmar pago: {e}")
            return False, 'Error al confirmar el pago'

    def cancelar_orden(self, orden_id, cliente_id=None):
        """Cancela una orden pendiente (pago abandonado o rechazado)."""
        try:
            query = self.session.query(Orden).filter_by(id_orden=orden_id, estado='pendiente')
            if cliente_id is not None:
                query = query.filter_by(id_cliente=cliente_id)
            orden = query.first()
            if not orden:
                return False
            orden.estado = 'cancelada'
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            logging.error(f"Error al cancelar orden: {e}")
            return False

    def get_by_id(self, orden_id):
        return self.session.query(Orden).filter_by(id_orden=orden_id).first()

    def get_by_id_for_cliente(self, orden_id, cliente_id):
        return self.session.query(Orden).filter_by(
            id_orden=orden_id,
            id_cliente=cliente_id,
        ).first()

    def crear_orden(self, cliente_id, direccion_id, total, items):
        """
        Compatibilidad: crea orden pendiente y la confirma al instante (sin pasarela).
        """
        exito, orden = self.crear_orden_pendiente(cliente_id, direccion_id, total, items)
        if not exito or not orden:
            return False, None
        ok, result = self.confirmar_pago(
            orden.id_orden,
            proveedor='legacy',
            referencia=f'legacy-{orden.id_orden}',
            monto=total,
        )
        if ok:
            return True, result if isinstance(result, Orden) else orden
        return False, None

    def get_by_usuario(self, usuario_id):
        return self.session.query(Orden).filter_by(id_cliente=usuario_id).order_by(desc(Orden.fecha_creacion)).all()

    def get_count_by_usuario(self, usuario_id):
        return self.session.query(Orden).filter_by(id_cliente=usuario_id).count()
