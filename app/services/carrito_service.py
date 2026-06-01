"""
Servicio de carrito de compras persistente en base de datos.
"""
from flask import session


class CarritoService:
    """Carrito de compras por usuario (PostgreSQL)."""

    def __init__(self, carrito_repo=None, producto_repo=None):
        self.carrito_repo = carrito_repo
        self.producto_repo = producto_repo

    def _session_cart(self):
        """Carrito legacy en sesión (solo para fusionar al iniciar sesión)."""
        if 'carrito' not in session:
            session['carrito'] = {}
        return session['carrito']

    def fusionar_sesion(self, usuario_id):
        """Fusionar carrito de sesión (legacy) con el persistente del usuario."""
        carrito_sesion = self._session_cart()
        if not carrito_sesion or not self.carrito_repo:
            return True

        for producto_id_str, cantidad in carrito_sesion.items():
            try:
                cantidad = int(cantidad)
                if cantidad <= 0:
                    continue
                self.carrito_repo.add_or_increment(usuario_id, int(producto_id_str), cantidad)
            except (TypeError, ValueError):
                continue

        session.pop('carrito', None)
        session.modified = True
        return self.carrito_repo.save()

    def agregar_producto(self, usuario_id, producto_id, cantidad=1):
        if not self.carrito_repo or cantidad < 1:
            return False
        item = self.carrito_repo.add_or_increment(usuario_id, producto_id, cantidad)
        if not item:
            return False
        return self.carrito_repo.save()

    def remover_producto(self, usuario_id, producto_id):
        if not self.carrito_repo:
            return False
        if not self.carrito_repo.remove_item(usuario_id, producto_id):
            return False
        return self.carrito_repo.save()

    def actualizar_cantidad(self, usuario_id, producto_id, cantidad):
        if cantidad <= 0:
            return self.remover_producto(usuario_id, producto_id)
        if not self.carrito_repo:
            return False
        item = self.carrito_repo.set_cantidad(usuario_id, producto_id, cantidad)
        if not item:
            return False
        return self.carrito_repo.save()

    def vaciar_carrito(self, usuario_id):
        if not self.carrito_repo:
            return False
        if not self.carrito_repo.clear_usuario(usuario_id):
            return False
        return self.carrito_repo.save()

    def get_items(self, usuario_id):
        items = []
        total = 0

        if not self.carrito_repo or not self.producto_repo:
            return items, total

        for row in self.carrito_repo.get_items_by_usuario(usuario_id):
            producto = self.producto_repo.get_by_id(row.id_producto)
            if producto:
                subtotal = float(producto.precio) * row.cantidad
                total += subtotal
                items.append({
                    'producto': producto,
                    'cantidad': row.cantidad,
                    'subtotal': subtotal,
                })

        return items, total

    def get_count(self, usuario_id):
        if not self.carrito_repo:
            return 0
        return self.carrito_repo.get_total_count(usuario_id)
