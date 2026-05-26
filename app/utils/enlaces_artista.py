"""Enlaces públicos del perfil de artista (redes y sitio web)."""


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
    instagram = normalizar_url_enlace(getattr(usuario, 'enlace_instagram', None))
    if instagram:
        items.append({
            'url': instagram,
            'label': 'Instagram',
            'icon': 'fab fa-instagram',
        })

    web = normalizar_url_enlace(getattr(usuario, 'enlace_web', None))
    if web:
        items.append({
            'url': web,
            'label': 'Sitio web',
            'icon': 'fas fa-globe',
        })

    extra_url = normalizar_url_enlace(getattr(usuario, 'enlace_extra_url', None))
    if extra_url:
        etiqueta = _limpiar_campo(getattr(usuario, 'enlace_extra_etiqueta', None)) or 'Enlace'
        items.append({
            'url': extra_url,
            'label': etiqueta,
            'icon': 'fas fa-link',
        })

    return items
