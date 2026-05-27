"""Enlaces públicos del perfil de artista (redes y sitio web)."""
from urllib.parse import urlparse

_PLATAFORMAS = (
    ('instagram.com', 'Instagram', 'fab fa-instagram'),
    ('pinterest.com', 'Pinterest', 'fab fa-pinterest'),
    ('pin.it', 'Pinterest', 'fab fa-pinterest'),
    ('behance.net', 'Behance', 'fab fa-behance'),
    ('tiktok.com', 'TikTok', 'fab fa-tiktok'),
    ('twitter.com', 'X', 'fab fa-x-twitter'),
    ('x.com', 'X', 'fab fa-x-twitter'),
    ('facebook.com', 'Facebook', 'fab fa-facebook'),
    ('youtube.com', 'YouTube', 'fab fa-youtube'),
    ('youtu.be', 'YouTube', 'fab fa-youtube'),
    ('vimeo.com', 'Vimeo', 'fab fa-vimeo'),
    ('linkedin.com', 'LinkedIn', 'fab fa-linkedin'),
    ('artstation.com', 'ArtStation', 'fab fa-artstation'),
    ('dribbble.com', 'Dribbble', 'fab fa-dribbble'),
    ('deviantart.com', 'DeviantArt', 'fab fa-deviantart'),
    ('github.com', 'GitHub', 'fab fa-github'),
)


def normalizar_url_enlace(valor):
    if not valor or not str(valor).strip():
        return None
    texto = str(valor).strip()
    if texto.startswith('@'):
        return f'https://instagram.com/{texto[1:].strip("/")}'
    if not texto.startswith(('http://', 'https://')):
        texto = f'https://{texto}'
    return texto


def _limpiar_campo(valor):
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


def _parece_url(texto):
    t = str(texto).strip().lower()
    return t.startswith(('http://', 'https://', 'www.')) or ('.' in t and ' ' not in t)


def _detectar_plataforma(url):
    url_lower = (url or '').lower()
    for dominio, nombre, icono in _PLATAFORMAS:
        if dominio in url_lower:
            return nombre, icono
    return None, None


def _etiqueta_para_url(url, etiqueta_manual=None, etiqueta_por_defecto='Enlace'):
    if etiqueta_manual and not _parece_url(etiqueta_manual):
        return etiqueta_manual
    nombre, _ = _detectar_plataforma(url)
    if nombre:
        return nombre
    if etiqueta_por_defecto and etiqueta_por_defecto != 'Enlace':
        return etiqueta_por_defecto
    host = urlparse(url).netloc.replace('www.', '')
    return host or 'Enlace'


def _icono_para_url(url, icono_por_defecto='fas fa-link'):
    _, icono = _detectar_plataforma(url)
    return icono or icono_por_defecto


def enlaces_desde_formulario(form):
    """Extrae y normaliza enlaces del formulario de perfil."""
    return {
        'enlace_instagram': _limpiar_campo(form.get('enlace_instagram')),
        'enlace_web': _limpiar_campo(form.get('enlace_web')),
        'enlace_extra_url': _limpiar_campo(form.get('enlace_extra_url')),
        'enlace_extra_etiqueta': _limpiar_campo(form.get('enlace_extra_etiqueta')),
    }


def listar_enlaces_artista(usuario):
    """Lista de enlaces listos para mostrar en plantillas."""
    if usuario is None:
        return []

    items = []
    vistos = set()

    def agregar(raw, etiqueta_defecto, icono_defecto):
        url = normalizar_url_enlace(raw)
        if not url or url in vistos:
            return
        vistos.add(url)
        items.append({
            'url': url,
            'label': _etiqueta_para_url(url, etiqueta_por_defecto=etiqueta_defecto),
            'icon': _icono_para_url(url, icono_defecto),
        })

    agregar(getattr(usuario, 'enlace_instagram', None), 'Instagram', 'fab fa-instagram')
    agregar(getattr(usuario, 'enlace_web', None), 'Sitio web', 'fas fa-globe')

    etiqueta = _limpiar_campo(getattr(usuario, 'enlace_extra_etiqueta', None))
    extra_url_raw = _limpiar_campo(getattr(usuario, 'enlace_extra_url', None))

    # Si pegaron una URL en "nombre corto", también cuenta como enlace propio
    if etiqueta and _parece_url(etiqueta):
        agregar(etiqueta, 'Enlace', 'fas fa-link')

    if extra_url_raw:
        url = normalizar_url_enlace(extra_url_raw)
        if url and url not in vistos:
            vistos.add(url)
            etiqueta_texto = etiqueta if etiqueta and not _parece_url(etiqueta) else None
            items.append({
                'url': url,
                'label': _etiqueta_para_url(url, etiqueta_texto, 'Enlace'),
                'icon': _icono_para_url(url, 'fas fa-link'),
            })

    return items
