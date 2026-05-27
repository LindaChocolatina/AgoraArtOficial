from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.factories.service_factory import get_service_factory
from app.factories.app_factory import db
from app.models.obra_imagen import ObraImagen
from app.models.producto_imagen import ProductoImagen
from app.utils.file_upload import save_image_file, save_multiple_images
from app.utils.moneda import normalizar_moneda
from app.utils.perfil_usuario import foto_perfil_desde_form
from app.utils.obra_galeria import (
    asegurar_galeria_migrada,
    agregar_imagenes_galeria,
    eliminar_imagen_galeria,
    establecer_portada,
    guardar_galeria_completa,
    listar_imagenes_obra,
)
from app.utils.producto_galeria import (
    agregar_imagenes_galeria as agregar_imgs_producto,
    asegurar_galeria_migrada as asegurar_galeria_producto,
    eliminar_imagen_galeria as eliminar_imagen_producto_galeria,
    establecer_portada as establecer_portada_producto,
    guardar_galeria_completa as guardar_galeria_producto,
    listar_imagenes_producto,
)
from functools import wraps


def _categoria_id_from_form():
    raw = request.form.get('categoria')
    return int(raw) if raw else None


def _guardar_imagenes_obra(obra_id, imagen_principal=None):
    """Guarda imágenes extra en la galería (la principal va en obra.imagen)."""
    extras = request.files.getlist('imagenes_extra')
    paths = save_multiple_images(extras, current_app.config['UPLOAD_FOLDER'], 'obras')
    for i, path in enumerate(paths):
        if imagen_principal and path == imagen_principal:
            continue
        db.session.add(ObraImagen(id_obra=obra_id, imagen=path, orden=i + 1))
    db.session.commit()


def _moneda_from_form():
    return normalizar_moneda(request.form.get('moneda'))


def _imagen_producto_desde_form():
    """Imagen de producto: archivo subido o ruta/URL en texto."""
    archivo = request.files.get('imagen_archivo')
    path = save_image_file(archivo, current_app.config['UPLOAD_FOLDER'], 'productos')
    if path:
        return path
    url = (request.form.get('imagen') or '').strip()
    return url or None

# Crear blueprint
artista_bp = Blueprint('artista', __name__)

def requiere_artista(f):
    """Decorador para requerir rol de artista"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_artista():
            flash('Esta página es solo para artistas', 'error')
            return redirect(url_for('public.home'))
        return f(*args, **kwargs)
    return decorated_function

@artista_bp.route('/dashboard')
@login_required
@requiere_artista
def dashboard():
    """
    Dashboard del artista (Estilo Behance Profesional)
    """
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    producto_service = service_factory.get_producto_service()
    usuario_service = service_factory.get_usuario_service()
    categoria_service = service_factory.get_categoria_service()
    blog_service = service_factory.get_blog_service()
    
    # Obtener estadísticas del artista
    stats = {
        'obras_count': obra_service.get_count_by_artista(current_user.id_usuario),
        'productos_count': producto_service.get_count_by_artista(current_user.id_usuario),
        'seguidores_count': usuario_service.get_seguidores_count(current_user.id_usuario),
        'siguiendo_count': usuario_service.get_siguiendo_count(current_user.id_usuario),
        'blog_count': blog_service.get_count_by_artista(current_user.id_usuario),
        'vistas_proyectos': 1250, # Placeholder para MVP
        'valoraciones': 84
    }
    
    # Obtener obras (Portfolio)
    obras = obra_service.get_by_artista(current_user.id_usuario, visible_only=False)
    
    # Obtener categorías para filtro
    categorias = categoria_service.get_all()
    
    # Obtener productos (Tienda)
    productos = producto_service.get_by_artista(current_user.id_usuario, disponibles_only=False)
    
    # Obtener entradas de blog reales
    entradas_blog = blog_service.get_by_artista(current_user.id_usuario)

    ultima_obra = obras[0] if obras else None
    ultima_entrada = entradas_blog[0] if entradas_blog else None
    ultimo_producto = productos[0] if productos else None

    perfil = usuario_service.get_by_id(current_user.id_usuario)
    
    return render_template('artista/dashboard.html',
                         stats=stats,
                         obras=obras,
                         productos=productos,
                         entradas_blog=entradas_blog,
                         categorias=categorias,
                         ultima_obra=ultima_obra,
                         ultima_entrada=ultima_entrada,
                         ultimo_producto=ultimo_producto,
                         banner_perfil=perfil.banner_perfil if perfil else None,
                         banner_offset=perfil.banner_offset if perfil and perfil.banner_offset is not None else 50)

@artista_bp.route('/banner', methods=['GET', 'POST'])
@login_required
@requiere_artista
def editar_banner():
    """Subir o cambiar el banner del panel del artista."""
    service_factory = get_service_factory()
    usuario_service = service_factory.get_usuario_service()
    perfil = usuario_service.get_by_id(current_user.id_usuario)

    if request.method == 'POST':
        try:
            offset_val = int(request.form.get('banner_offset', 50))
            offset_val = max(0, min(100, offset_val))
        except (TypeError, ValueError):
            offset_val = 50

        path = save_image_file(
            request.files.get('banner'),
            current_app.config['UPLOAD_FOLDER'],
            'banners',
        )
        datos = {'banner_offset': offset_val}
        if path:
            datos['banner_perfil'] = path

        if path or (perfil and perfil.banner_perfil):
            exitoso, _ = usuario_service.actualizar_usuario(
                current_user.id_usuario,
                datos,
            )
            if exitoso:
                flash('Banner actualizado.', 'success')
                return redirect(url_for('artista.dashboard'))
            flash('No se pudo guardar el banner.', 'error')
        else:
            flash('Sube una imagen de banner la primera vez.', 'error')

    return render_template(
        'artista/editar_banner.html',
        banner_offset=perfil.banner_offset if perfil and perfil.banner_offset is not None else 50,
    )


@artista_bp.route('/foto-perfil', methods=['GET', 'POST'])
@login_required
@requiere_artista
def editar_foto_perfil():
    """Subir, cambiar o quitar la foto de perfil del artista."""
    service_factory = get_service_factory()
    usuario_service = service_factory.get_usuario_service()

    if request.method == 'POST':
        datos = foto_perfil_desde_form(request, current_app.config['UPLOAD_FOLDER'])
        if not datos:
            flash('Selecciona una imagen o marca quitar la foto actual.', 'error')
        else:
            exitoso, _ = usuario_service.actualizar_usuario(current_user.id_usuario, datos)
            if exitoso:
                flash('Foto de perfil actualizada.', 'success')
                return redirect(url_for('artista.dashboard'))
            flash('No se pudo guardar la foto.', 'error')

    return render_template('artista/editar_foto_perfil.html')


@artista_bp.route('/perfil')
@login_required
@requiere_artista
def perfil():
    """
    Perfil del artista
    """
    return render_template('artista/perfil.html')

@artista_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
@requiere_artista
def editar_perfil():
    """
    Editar perfil del artista
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        data = {
            'nombre': request.form.get('nombre'),
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'biografia': request.form.get('biografia', ''),
            'ubicacion': request.form.get('ubicacion', '').strip() or None
        }
        from app.utils.enlaces_artista import enlaces_desde_formulario
        data.update(enlaces_desde_formulario(request.form))
        data.update(foto_perfil_desde_form(request, current_app.config['UPLOAD_FOLDER']))
        
        # Validar y actualizar
        service_factory = get_service_factory()
        usuario_service = service_factory.get_usuario_service()
        
        exitoso, usuario_actualizado = usuario_service.actualizar_usuario(current_user.id_usuario, data)
        
        if exitoso:
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('artista.perfil'))
        else:
            flash('Error al actualizar el perfil', 'error')
    
    return render_template('artista/editar_perfil.html')

@artista_bp.route('/obras')
@login_required
@requiere_artista
def obras():
    """
    Listado de obras del artista
    """
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    
    # Obtener obras del artista
    obras = obra_service.get_by_artista(current_user.id_usuario, visible_only=False)
    
    return render_template('artista/obras.html', obras=obras)

@artista_bp.route('/obras/nueva', methods=['GET', 'POST'])
@login_required
@requiere_artista
def nueva_obra():
    """
    Crear nueva obra
    """
    if request.method == 'POST':
        imagenes = save_multiple_images(
            request.files.getlist('imagenes'),
            current_app.config['UPLOAD_FOLDER'],
            'obras',
        )
        data = {
            'id_artista': current_user.id_usuario,
            'titulo': request.form.get('titulo'),
            'descripcion': request.form.get('descripcion', ''),
            'tecnica': request.form.get('tecnica', ''),
            'id_categoria': _categoria_id_from_form(),
            'visible': request.form.get('visible') == 'on',
            'imagen': imagenes[0] if imagenes else '/static/uploads/obra1.jpg',
        }

        errores = []
        if not data.get('titulo', '').strip():
            errores.append('El título es obligatorio')
        if not imagenes:
            errores.append('Al menos una imagen es obligatoria')

        if not errores:
            service_factory = get_service_factory()
            obra_service = service_factory.get_obra_service()
            exitoso, obra_creada = obra_service.crear_obra(data)

            if exitoso:
                guardar_galeria_completa(obra_creada.id_obra, imagenes)
                flash(f'Proyecto publicado con {len(imagenes)} imagen(es).', 'success')
                return redirect(url_for('artista.obras'))
            flash('Error al crear la obra', 'error')
        else:
            for error in errores:
                flash(error, 'error')
    
    # Obtener categorías para el formulario
    service_factory = get_service_factory()
    categoria_service = service_factory.get_categoria_service()
    categorias = categoria_service.get_all()
    
    return render_template('artista/nueva_obra.html', categorias=categorias)

@artista_bp.route('/obras/<int:obra_id>/editar', methods=['GET', 'POST'])
@login_required
@requiere_artista
def editar_obra(obra_id):
    """
    Editar obra existente
    """
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    
    # Obtener obra
    obra = obra_service.get_by_id(obra_id)
    
    if not obra or obra.id_artista != current_user.id_usuario:
        flash('Obra no encontrada o no tienes permisos', 'error')
        return redirect(url_for('artista.obras'))
    
    if request.method == 'POST':
        data = {
            'titulo': request.form.get('titulo'),
            'descripcion': request.form.get('descripcion', ''),
            'tecnica': request.form.get('tecnica', ''),
            'id_categoria': _categoria_id_from_form(),
            'visible': request.form.get('visible') == 'on',
        }

        nuevas = save_multiple_images(
            request.files.getlist('imagenes'),
            current_app.config['UPLOAD_FOLDER'],
            'obras',
        )

        errores = []
        if not data.get('titulo', '').strip():
            errores.append('El título es obligatorio')

        if not errores:
            exitoso, obra_actualizada = obra_service.actualizar_obra(obra_id, data)
            if exitoso:
                if nuevas:
                    agregar_imagenes_galeria(obra_id, nuevas)
                flash('Obra actualizada correctamente', 'success')
                return redirect(url_for('artista.obras'))
            flash('Error al actualizar la obra', 'error')
        else:
            for error in errores:
                flash(error, 'error')

    categoria_service = service_factory.get_categoria_service()
    categorias = categoria_service.get_all()
    asegurar_galeria_migrada(obra)
    galeria = listar_imagenes_obra(obra)

    return render_template('artista/editar_obra.html', obra=obra, categorias=categorias, galeria=galeria)


@artista_bp.route('/obras/<int:obra_id>/imagenes/subir', methods=['POST'])
@login_required
@requiere_artista
def subir_imagenes_obra(obra_id):
    """Sube varias fotos de golpe sin guardar el resto del formulario."""
    obra = get_service_factory().get_obra_service().get_by_id(obra_id)
    if not obra or obra.id_artista != current_user.id_usuario:
        return jsonify({'error': 'Sin permisos'}), 403
    paths = save_multiple_images(
        request.files.getlist('imagenes'),
        current_app.config['UPLOAD_FOLDER'],
        'obras',
    )
    if not paths:
        return jsonify({'error': 'No se recibieron imágenes válidas'}), 400
    agregar_imagenes_galeria(obra_id, paths)
    from app.utils.obra_galeria import contar_imagenes_obra
    return jsonify({
        'ok': True,
        'count': len(paths),
        'total': contar_imagenes_obra(obra),
    })


@artista_bp.route('/obras/<int:obra_id>/imagen/<int:id_imagen>/eliminar', methods=['POST'])
@login_required
@requiere_artista
def eliminar_imagen_obra(obra_id, id_imagen):
    obra = get_service_factory().get_obra_service().get_by_id(obra_id)
    if not obra or obra.id_artista != current_user.id_usuario:
        flash('Sin permisos', 'error')
        return redirect(url_for('artista.obras'))
    eliminar_imagen_galeria(obra_id, id_imagen)
    flash('Imagen eliminada', 'success')
    return redirect(url_for('artista.editar_obra', obra_id=obra_id))


@artista_bp.route('/obras/<int:obra_id>/imagen/<int:id_imagen>/portada', methods=['POST'])
@login_required
@requiere_artista
def portada_imagen_obra(obra_id, id_imagen):
    obra = get_service_factory().get_obra_service().get_by_id(obra_id)
    if not obra or obra.id_artista != current_user.id_usuario:
        flash('Sin permisos', 'error')
        return redirect(url_for('artista.obras'))
    if establecer_portada(obra_id, id_imagen):
        flash('Portada actualizada', 'success')
    return redirect(url_for('artista.editar_obra', obra_id=obra_id))

def _redirect_tras_accion(fallback='artista.dashboard'):
    """Vuelve al dashboard si la acción venía de ahí."""
    ref = request.referrer or ''
    if 'dashboard' in ref:
        return redirect(url_for('artista.dashboard'))
    return redirect(url_for(fallback))


@artista_bp.route('/obras/<int:obra_id>/eliminar', methods=['POST'])
@login_required
@requiere_artista
def eliminar_obra(obra_id):
    """
    Eliminar obra
    """
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    
    # Verificar que la obra pertenezca al artista
    obra = obra_service.get_by_id(obra_id)
    
    if not obra or obra.id_artista != current_user.id_usuario:
        flash('Obra no encontrada o no tienes permisos', 'error')
        return redirect(url_for('artista.obras'))
    
    # Eliminar obra
    exitoso = obra_service.eliminar_obra(obra_id, current_user.id_usuario)
    
    if exitoso:
        flash('Obra eliminada correctamente', 'success')
    else:
        flash('Error al eliminar la obra', 'error')
    
    return _redirect_tras_accion('artista.obras')

@artista_bp.route('/productos')
@login_required
@requiere_artista
def productos():
    """
    Listado de productos del artista
    """
    service_factory = get_service_factory()
    producto_service = service_factory.get_producto_service()
    
    # Obtener productos del artista
    productos = producto_service.get_by_artista(current_user.id_usuario, disponibles_only=False)
    
    return render_template('artista/productos.html', productos=productos)

@artista_bp.route('/seguidores')
@login_required
@requiere_artista
def seguidores():
    """
    Listado de seguidores
    """
    service_factory = get_service_factory()
    usuario_service = service_factory.get_usuario_service()
    
    # Obtener seguidores
    seguidores = usuario_service.get_seguidores(current_user.id_usuario)
    
    return render_template('artista/seguidores.html', seguidores=seguidores)

@artista_bp.route('/blog/subir-imagen', methods=['POST'])
@login_required
@requiere_artista
def subir_imagen_blog():
    """Subir imagen para insertar en el editor del blog (Quill)."""
    path = save_image_file(
        request.files.get('imagen'),
        current_app.config['UPLOAD_FOLDER'],
        'blog',
    )
    if not path:
        return jsonify({'error': 'Archivo no válido'}), 400
    return jsonify({'url': path})


@artista_bp.route('/blog')
@login_required
@requiere_artista
def blog():
    """
    Blog del artista
    """
    service_factory = get_service_factory()
    blog_service = service_factory.get_blog_service()
    entradas = blog_service.get_by_artista(current_user.id_usuario)
    return render_template('artista/blog.html', entradas=entradas)

@artista_bp.route('/blog/nueva', methods=['GET', 'POST'])
@login_required
@requiere_artista
def nueva_entrada():
    """Crear nueva entrada de blog"""
    if request.method == 'POST':
        contenido = (request.form.get('contenido') or '').strip()
        data = {
            'id_artista': current_user.id_usuario,
            'titulo': request.form.get('titulo'),
            'contenido': contenido or '<p></p>',
            'visible': 'publicado' in request.form,
        }
        if not data['titulo'] or not contenido or contenido == '<p><br></p>':
            flash('Título y contenido son obligatorios', 'error')
        else:
            service_factory = get_service_factory()
            blog_service = service_factory.get_blog_service()
            exitoso, entrada = blog_service.crear_entrada(data)
            if exitoso:
                flash('Entrada de blog creada correctamente', 'success')
                return redirect(url_for('artista.blog'))
            flash('Error al crear la entrada. Verifica los campos.', 'error')
    return render_template('artista/nueva_entrada.html')

@artista_bp.route('/blog/<int:entrada_id>/editar', methods=['GET', 'POST'])
@login_required
@requiere_artista
def editar_entrada(entrada_id):
    """Editar entrada de blog"""
    service_factory = get_service_factory()
    blog_service = service_factory.get_blog_service()
    entrada = blog_service.get_by_id(entrada_id)
    if not entrada or entrada.id_artista != current_user.id_usuario:
        flash('Entrada no encontrada o no tienes permisos', 'error')
        return redirect(url_for('artista.blog'))
    if request.method == 'POST':
        data = {
            'titulo': request.form.get('titulo'),
            'contenido': request.form.get('contenido'),
            'visible': 'publicado' in request.form
        }
        exitoso, entrada_act = blog_service.actualizar_entrada(entrada_id, data)
        if exitoso:
            flash('Entrada actualizada correctamente', 'success')
            return redirect(url_for('artista.blog'))
        else:
            flash('Error al actualizar la entrada', 'error')
    return render_template('artista/editar_entrada.html', entrada=entrada)

@artista_bp.route('/blog/<int:entrada_id>/eliminar', methods=['POST'])
@login_required
@requiere_artista
def eliminar_entrada(entrada_id):
    """Eliminar entrada de blog"""
    service_factory = get_service_factory()
    blog_service = service_factory.get_blog_service()
    entrada = blog_service.get_by_id(entrada_id)
    if not entrada or entrada.id_artista != current_user.id_usuario:
        flash('Entrada no encontrada o no tienes permisos', 'error')
        return redirect(url_for('artista.blog'))
    if blog_service.eliminar_entrada(entrada_id):
        flash('Entrada eliminada correctamente', 'success')
    else:
        flash('Error al eliminar la entrada', 'error')
    return _redirect_tras_accion('artista.blog')

@artista_bp.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
@requiere_artista
def nuevo_producto():
    """Crear nuevo producto"""
    if request.method == 'POST':
        try:
            precio = float(request.form.get('precio', 0))
            stock = int(request.form.get('stock', 1))
        except (TypeError, ValueError):
            flash('Precio y stock deben ser números válidos', 'error')
            return render_template('artista/nuevo_producto.html')

        # Guardar múltiples imágenes si vienen
        imagenes_paths = save_multiple_images(
            request.files.getlist('imagenes'),
            current_app.config['UPLOAD_FOLDER'],
            'productos'
        )

        data = {
            'id_artista': current_user.id_usuario,
            'nombre': request.form.get('nombre'),
            'descripcion': request.form.get('descripcion', ''),
            'precio': precio,
            'moneda': _moneda_from_form(),
            'stock': stock,
            'imagen': imagenes_paths[0] if imagenes_paths else (_imagen_producto_desde_form() or ''),
        }
        service_factory = get_service_factory()
        producto_service = service_factory.get_producto_service()
        exitoso, producto = producto_service.crear_producto(data, current_user.id_usuario)
        if exitoso:
            if imagenes_paths:
                guardar_galeria_producto(producto.id_producto, imagenes_paths)
            flash('Producto creado correctamente', 'success')
            return redirect(url_for('artista.productos'))
        flash('Error al crear el producto. Verifica nombre, precio y stock.', 'error')
    return render_template('artista/nuevo_producto.html')

@artista_bp.route('/productos/<int:producto_id>/editar', methods=['GET', 'POST'])
@login_required
@requiere_artista
def editar_producto(producto_id):
    """Editar producto existente"""
    service_factory = get_service_factory()
    producto_service = service_factory.get_producto_service()
    producto = producto_service.get_by_id(producto_id)
    if not producto or producto.id_artista != current_user.id_usuario:
        flash('Producto no encontrado o no tienes permisos', 'error')
        return redirect(url_for('artista.productos'))
    if request.method == 'POST':
        try:
            precio = float(request.form.get('precio', 0))
            stock = int(request.form.get('stock', 0))
        except (TypeError, ValueError):
            flash('Precio y stock deben ser números válidos', 'error')
            return render_template('artista/editar_producto.html', producto=producto)

        data = {
            'nombre': request.form.get('nombre'),
            'descripcion': request.form.get('descripcion', ''),
            'precio': precio,
            'moneda': _moneda_from_form(),
            'stock': stock,
        }
        # Guardar nuevas imágenes subidas
        nuevas_paths = save_multiple_images(
            request.files.getlist('imagenes'),
            current_app.config['UPLOAD_FOLDER'],
            'productos'
        )

        exitoso, producto_act = producto_service.actualizar_producto(
            producto_id, data, current_user.id_usuario
        )
        if exitoso:
            if nuevas_paths:
                agregar_imgs_producto(producto_id, nuevas_paths)
            flash('Producto actualizado (stock guardado en base de datos)', 'success')
            return redirect(url_for('artista.productos'))
        flash('Error al actualizar el producto', 'error')
    asegurar_galeria_producto(producto)
    galeria = listar_imagenes_producto(producto)
    return render_template('artista/editar_producto.html', producto=producto, galeria=galeria)


@artista_bp.route('/productos/<int:producto_id>/imagenes/subir', methods=['POST'])
@login_required
@requiere_artista
def subir_imagenes_producto(producto_id):
    producto = get_service_factory().get_producto_service().get_by_id(producto_id)
    if not producto or producto.id_artista != current_user.id_usuario:
        return jsonify({'error': 'Sin permisos'}), 403
    paths = save_multiple_images(
        request.files.getlist('imagenes'),
        current_app.config['UPLOAD_FOLDER'],
        'productos',
    )
    if not paths:
        return jsonify({'error': 'No se recibieron imágenes válidas'}), 400
    agregar_imgs_producto(producto_id, paths)
    from app.utils.producto_galeria import contar_imagenes_producto
    return jsonify({'ok': True, 'count': len(paths), 'total': contar_imagenes_producto(producto)})


@artista_bp.route('/productos/<int:producto_id>/imagen/<int:id_imagen>/eliminar', methods=['POST'])
@login_required
@requiere_artista
def eliminar_imagen_producto(producto_id, id_imagen):
    producto = get_service_factory().get_producto_service().get_by_id(producto_id)
    if not producto or producto.id_artista != current_user.id_usuario:
        flash('Sin permisos', 'error')
        return redirect(url_for('artista.productos'))
    eliminar_imagen_producto_galeria(producto_id, id_imagen)
    flash('Imagen eliminada', 'success')
    return redirect(url_for('artista.editar_producto', producto_id=producto_id))


@artista_bp.route('/productos/<int:producto_id>/imagen/<int:id_imagen>/portada', methods=['POST'])
@login_required
@requiere_artista
def portada_imagen_producto(producto_id, id_imagen):
    producto = get_service_factory().get_producto_service().get_by_id(producto_id)
    if not producto or producto.id_artista != current_user.id_usuario:
        flash('Sin permisos', 'error')
        return redirect(url_for('artista.productos'))
    if establecer_portada_producto(producto_id, id_imagen):
        flash('Portada actualizada', 'success')
    return redirect(url_for('artista.editar_producto', producto_id=producto_id))

@artista_bp.route('/productos/<int:producto_id>/eliminar', methods=['POST'])
@login_required
@requiere_artista
def eliminar_producto(producto_id):
    """Eliminar producto"""
    service_factory = get_service_factory()
    producto_service = service_factory.get_producto_service()
    producto = producto_service.get_by_id(producto_id)
    if not producto or producto.id_artista != current_user.id_usuario:
        flash('Producto no encontrado o no tienes permisos', 'error')
        return redirect(url_for('artista.productos'))
    if producto_service.eliminar_producto(producto_id, current_user.id_usuario):
        flash('Producto eliminado correctamente', 'success')
    else:
        if producto.orden_items.count() > 0:
            flash('No se puede eliminar: este producto tiene ventas registradas.', 'error')
        else:
            flash('Error al eliminar el producto', 'error')
    return _redirect_tras_accion('artista.productos')

# API endpoints
@artista_bp.route('/api/toggle-visibilidad-obra', methods=['POST'])
@login_required
@requiere_artista
def toggle_visibilidad_obra():
    """
    API para cambiar visibilidad de obra
    """
    obra_id = request.json.get('obra_id')
    
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    
    # Verificar que la obra pertenezca al artista
    obra = obra_service.get_by_id(obra_id)
    
    if not obra or obra.id_artista != current_user.id_usuario:
        return jsonify({'error': 'No tienes permisos sobre esta obra'}), 403
    
    # Cambiar visibilidad
    exitoso, obra_actualizada = obra_service.toggle_visibilidad(obra_id)
    
    if exitoso:
        return jsonify({
            'exitoso': True,
            'visible': obra_actualizada.visible,
            'mensaje': 'Visibilidad actualizada correctamente'
        })
    else:
        return jsonify({
            'exitoso': False,
            'mensaje': 'Error al actualizar visibilidad'
        })
