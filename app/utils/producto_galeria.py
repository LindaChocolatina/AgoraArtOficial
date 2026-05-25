"""Galería de imágenes de productos (tienda)."""
from sqlalchemy import func

from app.factories.app_factory import db
from app.models.producto import Producto
from app.models.producto_imagen import ProductoImagen


def listar_imagenes_producto(producto):
    if not producto:
        return []
    rows = (
        ProductoImagen.query.filter_by(id_producto=producto.id_producto)
        .order_by(ProductoImagen.orden.asc(), ProductoImagen.id_imagen.asc())
        .all()
    )
    if rows:
        return [
            {'url': r.imagen, 'id_imagen': r.id_imagen, 'orden': r.orden}
            for r in rows
        ]
    if producto.imagen:
        return [{'url': producto.imagen, 'id_imagen': None, 'orden': 0}]
    return []


def asegurar_galeria_migrada(producto):
    if not producto or not producto.imagen:
        return
    if not ProductoImagen.query.filter_by(id_producto=producto.id_producto).first():
        db.session.add(ProductoImagen(
            id_producto=producto.id_producto, imagen=producto.imagen, orden=0
        ))
        db.session.commit()


def guardar_galeria_completa(producto_id, paths):
    if not paths:
        return
    producto = Producto.query.get(producto_id)
    if not producto:
        return
    for orden, path in enumerate(paths):
        db.session.add(ProductoImagen(id_producto=producto_id, imagen=path, orden=orden))
    producto.imagen = paths[0]
    db.session.commit()


def agregar_imagenes_galeria(producto_id, paths):
    if not paths:
        return
    asegurar_galeria_migrada(Producto.query.get(producto_id))
    max_orden = (
        db.session.query(func.max(ProductoImagen.orden))
        .filter_by(id_producto=producto_id)
        .scalar()
    )
    start = 0 if max_orden is None else int(max_orden) + 1
    producto = Producto.query.get(producto_id)
    for i, path in enumerate(paths):
        db.session.add(ProductoImagen(id_producto=producto_id, imagen=path, orden=start + i))
    if producto and not producto.imagen:
        producto.imagen = paths[0]
    db.session.commit()


def establecer_portada(producto_id, id_imagen):
    img = ProductoImagen.query.filter_by(id_producto=producto_id, id_imagen=id_imagen).first()
    producto = Producto.query.get(producto_id)
    if not img or not producto:
        return False
    producto.imagen = img.imagen
    resto = (
        ProductoImagen.query.filter(
            ProductoImagen.id_producto == producto_id,
            ProductoImagen.id_imagen != id_imagen,
        )
        .order_by(ProductoImagen.orden.asc())
        .all()
    )
    img.orden = 0
    for idx, row in enumerate(resto, start=1):
        row.orden = idx
    db.session.commit()
    return True


def eliminar_imagen_galeria(producto_id, id_imagen):
    img = ProductoImagen.query.filter_by(id_producto=producto_id, id_imagen=id_imagen).first()
    producto = Producto.query.get(producto_id)
    if not img or not producto:
        return False
    db.session.delete(img)
    db.session.flush()
    resto = (
        ProductoImagen.query.filter_by(id_producto=producto_id)
        .order_by(ProductoImagen.orden.asc())
        .all()
    )
    for idx, row in enumerate(resto):
        row.orden = idx
    if resto:
        producto.imagen = resto[0].imagen
    else:
        producto.imagen = None
    db.session.commit()
    return True


def contar_imagenes_producto(producto):
    n = ProductoImagen.query.filter_by(id_producto=producto.id_producto).count()
    if n:
        return n
    return 1 if producto.imagen else 0
