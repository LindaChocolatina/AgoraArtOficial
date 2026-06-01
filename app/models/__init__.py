"""
Importación de todos los modelos de la aplicación
"""

from app.models.usuario import Usuario, favoritos_obras, favoritos_artistas, bandeja_newsletter
from app.models.categoria import Categoria
from app.models.obra import Obra
from app.models.obra_imagen import ObraImagen
from app.models.producto import Producto, HistorialStock
from app.models.producto_imagen import ProductoImagen
from app.models.blog import EntradaBlog, ComentarioBlog
from app.models.ecommerce import Direccion, Orden, OrdenItem, Pago, CarritoItem
from app.models.moodboard import Lienzo, LienzoItem
from app.models.newsletter import Newsletter, Suscripcion
from app.models.auditoria import Auditoria

# Lista de todos los modelos para facilitar importaciones
__all__ = [
    'Usuario', 'favoritos_obras', 'favoritos_artistas', 'bandeja_newsletter',
    'Categoria',
    'Obra', 'ObraImagen',
    'Producto', 'HistorialStock', 'ProductoImagen',
    'EntradaBlog', 'ComentarioBlog',
    'Direccion', 'Orden', 'OrdenItem', 'Pago', 'CarritoItem',
    'Lienzo', 'LienzoItem',
    'Newsletter', 'Suscripcion',
    'Auditoria'
]