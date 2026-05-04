from app.models.ecommerce import Orden
from sqlalchemy import desc

class OrdenService:
    def __init__(self, session=None):
        self.session = session
        
    def crear_orden(self, cliente_id, direccion_id, total, items):
        """
        Crear una nueva orden con sus items
        
        Args:
            cliente_id (int): ID del cliente
            direccion_id (int): ID de la dirección de envío
            total (float): Total de la orden
            items (list): Lista de diccionarios con {'producto': producto_obj, 'cantidad': int}
            
        Returns:
            tuple: (bool, Orden) - (exitoso, orden_creada)
        """
        from app.models.ecommerce import Orden, OrdenItem
        from app.factories.service_factory import get_service_factory
        import logging

        try:
            # 1. Crear la orden principal
            nueva_orden = Orden(
                id_cliente=cliente_id,
                id_direccion=direccion_id,
                total=total,
                estado='pendiente'
            )
            self.session.add(nueva_orden)
            self.session.flush() # Para obtener el id_orden

            service_factory = get_service_factory(self.session)
            producto_service = service_factory.get_producto_service()

            # 2. Crear los items de la orden y actualizar stock
            for item in items:
                producto = item['producto']
                cantidad = item['cantidad']
                
                # Verificar stock antes de procesar
                if not producto_service.verificar_disponibilidad(producto.id_producto, cantidad):
                    self.session.rollback()
                    return False, None

                # Crear item de orden
                orden_item = OrdenItem(
                    id_orden=nueva_orden.id_orden,
                    id_producto=producto.id_producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio,
                    subtotal=float(producto.precio) * cantidad
                )
                self.session.add(orden_item)

                # Reducir stock
                exito_stock = producto_service.reducir_stock_venta(producto.id_producto, cantidad)
                if not exito_stock:
                    self.session.rollback()
                    return False, None

            # 3. Confirmar transacción
            self.session.commit()
            return True, nueva_orden

        except Exception as e:
            self.session.rollback()
            logging.error(f"Error al crear orden: {e}")
            return False, None
        
    def get_by_usuario(self, usuario_id):
        """Obtener historial de órdenes de un usuario"""
        return self.session.query(Orden).filter_by(id_cliente=usuario_id).order_by(desc(Orden.fecha_creacion)).all()
        
    def get_count_by_usuario(self, usuario_id):
        """Obtener cantidad de órdenes de un usuario"""
        return self.session.query(Orden).filter_by(id_cliente=usuario_id).count()
