"""Galería de imágenes de obras (estilo portafolio / Behance)."""
from sqlalchemy import func

from app.factories.app_factory import db
from app.models.obra import Obra
from app.models.obra_imagen import ObraImagen


def listar_imagenes_obra(obra):
    """Lista ordenada de imágenes: {url, id_imagen, orden}."""
    if not obra:
        return []
    rows = (
        ObraImagen.query.filter_by(id_obra=obra.id_obra)
        .order_by(ObraImagen.orden.asc(), ObraImagen.id_imagen.asc())
        .all()
    )
    if rows:
        return [
            {'url': r.imagen, 'id_imagen': r.id_imagen, 'orden': r.orden}
            for r in rows
        ]
    if obra.imagen:
        return [{'url': obra.imagen, 'id_imagen': None, 'orden': 0}]
    return []


def urls_obra(obra):
    return [i['url'] for i in listar_imagenes_obra(obra)]


def asegurar_galeria_migrada(obra):
    """Obras antiguas: copia la portada a la tabla de galería."""
    if not obra or not obra.imagen:
        return
    existe = ObraImagen.query.filter_by(id_obra=obra.id_obra).first()
    if not existe:
        db.session.add(ObraImagen(id_obra=obra.id_obra, imagen=obra.imagen, orden=0))
        db.session.commit()


def guardar_galeria_completa(obra_id, paths):
    """Guarda todas las rutas como galería; la primera es portada."""
    if not paths:
        return
    obra = Obra.query.get(obra_id)
    if not obra:
        return
    for orden, path in enumerate(paths):
        db.session.add(ObraImagen(id_obra=obra_id, imagen=path, orden=orden))
    obra.imagen = paths[0]
    db.session.commit()


def agregar_imagenes_galeria(obra_id, paths):
    """Añade imágenes al final de la galería existente."""
    if not paths:
        return
    asegurar_galeria_migrada(Obra.query.get(obra_id))
    max_orden = (
        db.session.query(func.max(ObraImagen.orden))
        .filter_by(id_obra=obra_id)
        .scalar()
    )
    start = 0 if max_orden is None else int(max_orden) + 1
    obra = Obra.query.get(obra_id)
    for i, path in enumerate(paths):
        db.session.add(ObraImagen(id_obra=obra_id, imagen=path, orden=start + i))
    if obra and not obra.imagen:
        obra.imagen = paths[0]
    db.session.commit()


def establecer_portada(obra_id, id_imagen):
    img = ObraImagen.query.filter_by(id_obra=obra_id, id_imagen=id_imagen).first()
    obra = Obra.query.get(obra_id)
    if not img or not obra:
        return False
    obra.imagen = img.imagen
    resto = (
        ObraImagen.query.filter(
            ObraImagen.id_obra == obra_id,
            ObraImagen.id_imagen != id_imagen,
        )
        .order_by(ObraImagen.orden.asc())
        .all()
    )
    img.orden = 0
    for idx, row in enumerate(resto, start=1):
        row.orden = idx
    db.session.commit()
    return True


def eliminar_imagen_galeria(obra_id, id_imagen):
    img = ObraImagen.query.filter_by(id_obra=obra_id, id_imagen=id_imagen).first()
    obra = Obra.query.get(obra_id)
    if not img or not obra:
        return False
    era_portada = obra.imagen == img.imagen
    db.session.delete(img)
    db.session.flush()
    resto = (
        ObraImagen.query.filter_by(id_obra=obra_id)
        .order_by(ObraImagen.orden.asc())
        .all()
    )
    for idx, row in enumerate(resto):
        row.orden = idx
    if resto:
        obra.imagen = resto[0].imagen
    else:
        obra.imagen = '/static/uploads/obra1.jpg'
    db.session.commit()
    return era_portada


def contar_imagenes_obra(obra):
    n = ObraImagen.query.filter_by(id_obra=obra.id_obra).count()
    if n:
        return n
    return 1 if obra.imagen else 0
