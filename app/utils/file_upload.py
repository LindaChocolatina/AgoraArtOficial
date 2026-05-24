"""Utilidades para subir archivos al servidor."""
import os
import uuid

from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def save_image_file(file_storage, upload_folder, subfolder=''):
    """
    Guarda un archivo de imagen y devuelve la ruta pública (/static/uploads/...).
    """
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_image(file_storage.filename):
        return None

    original = secure_filename(file_storage.filename)
    ext = original.rsplit('.', 1)[1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'

    dest_dir = os.path.join(upload_folder, subfolder) if subfolder else upload_folder
    os.makedirs(dest_dir, exist_ok=True)

    full_path = os.path.join(dest_dir, filename)
    file_storage.save(full_path)

    if subfolder:
        return f'/static/uploads/{subfolder}/{filename}'.replace('\\', '/')
    return f'/static/uploads/{filename}'.replace('\\', '/')


def save_multiple_images(files, upload_folder, subfolder=''):
    """Guarda varias imágenes; ignora las que no sean válidas."""
    paths = []
    for f in files or []:
        path = save_image_file(f, upload_folder, subfolder)
        if path:
            paths.append(path)
    return paths
