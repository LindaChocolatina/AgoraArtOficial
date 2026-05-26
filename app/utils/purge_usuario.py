"""Eliminación física de un usuario y sus datos relacionados."""

import os
from sqlalchemy import or_, delete

from app.factories.app_factory import db
from app.models.usuario import Usuario, favoritos_artistas, favoritos_obras, bandeja_newsletter
from app.models.obra import Obra
from app.models.obra_imagen import ObraImagen
from app.models.producto import Producto, HistorialStock
from app.models.producto_imagen import ProductoImagen
from app.models.ecommerce import OrdenItem
from app.models.blog import EntradaBlog, ComentarioBlog
from app.models.newsletter import Newsletter, Suscripcion
from app.models.moodboard import LienzoItem


def _unlink_static(path_value):
    if not path_value or not str(path_value).startswith('/static/'):
        return
    rel = str(path_value).replace('/static/', '').replace('/', os.sep)
    from flask import current_app
    full = os.path.join(current_app.root_path, 'static', rel)
    if os.path.isfile(full):
        try:
            os.remove(full)
        except OSError:
            pass


def purge_usuario_por_identificador(*, nombre=None, username=None, email=None):
    """
    Elimina un usuario y rastros en BD/archivos estáticos.
    Busca por nombre (parcial), username o email.
    """
    filters = []
    if nombre:
        filters.append(Usuario.nombre.ilike(f'%{nombre}%'))
    if username:
        filters.append(Usuario.username == username)
    if email:
        filters.append(Usuario.email == email)
    if not filters:
        return False, 'Sin criterio de búsqueda'

    usuario = Usuario.query.filter(or_(*filters)).first()
    if not usuario:
        return False, 'Usuario no encontrado'

    uid = usuario.id_usuario
    archivos = []
    if usuario.foto_perfil:
        archivos.append(usuario.foto_perfil)
    if usuario.banner_perfil:
        archivos.append(usuario.banner_perfil)

    db.session.execute(delete(favoritos_artistas).where(
        or_(favoritos_artistas.c.id_artista == uid, favoritos_artistas.c.id_usuario == uid)
    ))
    db.session.execute(delete(favoritos_obras).where(favoritos_obras.c.id_usuario == uid))
    db.session.execute(delete(Suscripcion).where(
        or_(Suscripcion.id_artista == uid, Suscripcion.id_cliente == uid)
    ))

    for nl in Newsletter.query.filter_by(id_artista=uid).all():
        db.session.execute(delete(bandeja_newsletter).where(bandeja_newsletter.c.id_newsletter == nl.id_newsletter))
        db.session.delete(nl)

    for obra in Obra.query.filter_by(id_artista=uid).all():
        archivos.append(obra.imagen)
        for img in ObraImagen.query.filter_by(id_obra=obra.id_obra).all():
            archivos.append(img.imagen)
            db.session.delete(img)
        db.session.execute(delete(favoritos_obras).where(favoritos_obras.c.id_obra == obra.id_obra))
        db.session.execute(delete(LienzoItem).where(LienzoItem.id_obra == obra.id_obra))
        db.session.delete(obra)

    for producto in Producto.query.filter_by(id_artista=uid).all():
        if OrdenItem.query.filter_by(id_producto=producto.id_producto).first():
            continue
        archivos.append(producto.imagen)
        for img in ProductoImagen.query.filter_by(id_producto=producto.id_producto).all():
            archivos.append(getattr(img, 'url', None) or getattr(img, 'imagen', None))
        db.session.execute(delete(HistorialStock).where(HistorialStock.id_producto == producto.id_producto))
        db.session.delete(producto)

    for entrada in EntradaBlog.query.filter_by(id_artista=uid).all():
        db.session.delete(entrada)

    ComentarioBlog.query.filter_by(id_usuario=uid).delete()

    db.session.delete(usuario)
    db.session.commit()

    for path in archivos:
        _unlink_static(path)

    return True, f'Usuario {uid} eliminado'
