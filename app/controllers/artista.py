from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.factories.service_factory import get_service_factory
from app.factories.app_factory import db
from app.models.obra_imagen import ObraImagen
from app.utils.file_upload import save_image_file, save_multiple_images
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


def _imagen_producto_desde_form():
    """Imagen de producto: archivo subido o URL."""
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
    
    return render_template('artista/dashboard.html',
                         stats=stats,
                         obras=obras,
                         productos=productos,
                         entradas_blog=entradas_blog,
                         categorias=categorias)

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
            'biografia': request.form.get('biografia', '')
        }
        
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
        imagen_principal = imagenes[0] if imagenes else '/static/uploads/obra1.jpg'

        data = {
            'id_artista': current_user.id_usuario,
            'titulo': request.form.get('titulo'),
            'descripcion': request.form.get('descripcion', ''),
            'tecnica': request.form.get('tecnica', ''),
            'id_categoria': _categoria_id_from_form(),
            'visible': request.form.get('visible') == 'on',
            'imagen': imagen_principal,
        }

        errores = []
        if not data.get('titulo', '').strip():
            errores.append('El título es obligatorio')

        if not errores:
            service_factory = get_service_factory()
            obra_service = service_factory.get_obra_service()
            exitoso, obra_creada = obra_service.crear_obra(data)

            if exitoso:
                for orden, path in enumerate(imagenes[1:], start=1):
                    db.session.add(ObraImagen(
                        id_obra=obra_creada.id_obra, imagen=path, orden=orden
                    ))
                db.session.commit()
                flash('Obra creada correctamente', 'success')
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
        if nuevas:
            data['imagen'] = nuevas[0]

        errores = []
        if not data.get('titulo', '').strip():
            errores.append('El título es obligatorio')

        if not errores:
            exitoso, obra_actualizada = obra_service.actualizar_obra(obra_id, data)
            if exitoso:
                max_orden = db.session.query(ObraImagen).filter_by(id_obra=obra_id).count()
                for i, path in enumerate(nuevas[1:] if nuevas else [], start=max_orden + 1):
                    db.session.add(ObraImagen(id_obra=obra_id, imagen=path, orden=i))
                db.session.commit()
                flash('Obra actualizada correctamente', 'success')
                return redirect(url_for('artista.obras'))
            flash('Error al actualizar la obra', 'error')
        else:
            for error in errores:
                flash(error, 'error')

    categoria_service = service_factory.get_categoria_service()
    categorias = categoria_service.get_all()
    galeria = list(obra.galeria_imagenes.all()) if hasattr(obra, 'galeria_imagenes') else []

    return render_template('artista/editar_obra.html', obra=obra, categorias=categorias, galeria=galeria)

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
    exitoso = obra_service.eliminar_obra(obra_id)
    
    if exitoso:
        flash('Obra eliminada correctamente', 'success')
    else:
        flash('Error al eliminar la obra', 'error')
    
    return redirect(url_for('artista.obras'))

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
    return redirect(url_for('artista.blog'))

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

        data = {
            'id_artista': current_user.id_usuario,
            'nombre': request.form.get('nombre'),
            'descripcion': request.form.get('descripcion', ''),
            'precio': precio,
            'stock': stock,
            'imagen': _imagen_producto_desde_form() or '',
        }
        service_factory = get_service_factory()
        producto_service = service_factory.get_producto_service()
        exitoso, producto = producto_service.crear_producto(data, current_user.id_usuario)
        if exitoso:
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
            'stock': stock,
        }
        nueva_imagen = _imagen_producto_desde_form()
        if nueva_imagen:
            data['imagen'] = nueva_imagen
        elif request.form.get('imagen'):
            data['imagen'] = request.form.get('imagen').strip()

        exitoso, producto_act = producto_service.actualizar_producto(
            producto_id, data, current_user.id_usuario
        )
        if exitoso:
            flash('Producto actualizado (stock guardado en base de datos)', 'success')
            return redirect(url_for('artista.productos'))
        flash('Error al actualizar el producto', 'error')
    return render_template('artista/editar_producto.html', producto=producto)

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
    if producto_service.eliminar_producto(producto_id):
        flash('Producto eliminado correctamente', 'success')
    else:
        flash('Error al eliminar el producto', 'error')
    return redirect(url_for('artista.productos'))

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
