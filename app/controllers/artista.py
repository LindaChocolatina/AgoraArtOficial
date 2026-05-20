from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.factories.service_factory import get_service_factory
from functools import wraps

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
        # Obtener datos del formulario
        data = {
            'id_artista': current_user.id_usuario,
            'titulo': request.form.get('titulo'),
            'descripcion': request.form.get('descripcion', ''),
            'tecnica': request.form.get('tecnica', ''),
            'id_categoria': request.form.get('categoria') or None,
            'visible': request.form.get('visible') == 'on'
        }
        
        # Validar datos
        errores = []
        if not data.get('titulo', '').strip():
            errores.append('El título es obligatorio')
        
        if not errores:
            service_factory = get_service_factory()
            obra_service = service_factory.get_obra_service()
            
            exitoso, obra_creada = obra_service.crear_obra(data)
            
            if exitoso:
                flash('Obra creada correctamente', 'success')
                return redirect(url_for('artista.obras'))
            else:
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
        # Obtener datos del formulario
        data = {
            'titulo': request.form.get('titulo'),
            'descripcion': request.form.get('descripcion', ''),
            'tecnica': request.form.get('tecnica', ''),
            'id_categoria': request.form.get('categoria') or None,
            'visible': request.form.get('visible') == 'on'
        }
        
        # Validar datos
        errores = []
        if not data.get('titulo', '').strip():
            errores.append('El título es obligatorio')
        
        if not errores:
            exitoso, obra_actualizada = obra_service.actualizar_obra(obra_id, data)
            
            if exitoso:
                flash('Obra actualizada correctamente', 'success')
                return redirect(url_for('artista.obras'))
            else:
                flash('Error al actualizar la obra', 'error')
        else:
            for error in errores:
                flash(error, 'error')
    
    # Obtener categorías para el formulario
    categoria_service = service_factory.get_categoria_service()
    categorias = categoria_service.get_all()
    
    return render_template('artista/editar_obra.html', obra=obra, categorias=categorias)

@artista_bp.route('/obras/<int:obra_id>/eliminar', methods=['POST'])
@login_required
@requiere_artista
def eliminar_obra(obra_id):
    """
    Eliminar obra
    """
    service_factory = get_service_factory()
    obra_service = obra_service = service_factory.get_obra_service()
    
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
        data = {
            'id_artista': current_user.id_usuario,
            'titulo': request.form.get('titulo'),
            'contenido': request.form.get('contenido'),
            'visible': 'publicado' in request.form
        }
        service_factory = get_service_factory()
        blog_service = service_factory.get_blog_service()
        exitoso, entrada = blog_service.crear_entrada(data)
        if exitoso:
            flash('Entrada de blog creada correctamente', 'success')
            return redirect(url_for('artista.blog'))
        else:
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
        data = {
            'id_artista': current_user.id_usuario,
            'nombre': request.form.get('nombre'),
            'descripcion': request.form.get('descripcion', ''),
            'precio': float(request.form.get('precio', 0)),
            'stock': int(request.form.get('stock', 1)),
            'imagen': request.form.get('imagen', '')
        }
        service_factory = get_service_factory()
        producto_service = service_factory.get_producto_service()
        exitoso, producto = producto_service.crear_producto(data)
        if exitoso:
            flash('Producto creado correctamente', 'success')
            return redirect(url_for('artista.productos'))
        else:
            flash('Error al crear el producto. Verifica los campos.', 'error')
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
        data = {
            'nombre': request.form.get('nombre'),
            'descripcion': request.form.get('descripcion', ''),
            'precio': float(request.form.get('precio', 0)),
            'stock': int(request.form.get('stock', 0)),
            'imagen': request.form.get('imagen', '')
        }
        exitoso, producto_act = producto_service.actualizar_producto(producto_id, data)
        if exitoso:
            flash('Producto actualizado correctamente', 'success')
            return redirect(url_for('artista.productos'))
        else:
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
