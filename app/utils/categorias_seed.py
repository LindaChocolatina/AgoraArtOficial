"""Siembra idempotente del catálogo de categorías."""

from app.utils.categorias_catalogo import CATEGORIAS_CATALOGO


def ensure_categorias_catalogo(session=None):
    """
    Inserta categorías del catálogo que aún no existan (por nombre único).
    """
    from app.factories.service_factory import get_service_factory

    service_factory = get_service_factory(session)
    categoria_service = service_factory.get_categoria_service()
    repo = categoria_service.categoria_repo

    creadas = 0
    for cat_data in CATEGORIAS_CATALOGO:
        if categoria_service.name_exists(cat_data['nombre']):
            continue
        if categoria_service.create(cat_data):
            creadas += 1

    if creadas:
        repo.save()

    return creadas
