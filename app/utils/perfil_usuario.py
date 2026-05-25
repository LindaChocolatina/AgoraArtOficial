"""Utilidades para foto de perfil de usuario."""
from app.utils.file_upload import save_image_file


def foto_perfil_desde_form(request, upload_folder):
    """
    Lee la foto enviada en el formulario o la opción de quitarla.

    Returns:
        dict: claves a fusionar en actualizar_usuario (puede estar vacío).
    """
    if request.form.get('quitar_foto'):
        return {'foto_perfil': None}

    path = save_image_file(
        request.files.get('foto_perfil'),
        upload_folder,
        'perfiles',
    )
    if path:
        return {'foto_perfil': path}
    return {}
