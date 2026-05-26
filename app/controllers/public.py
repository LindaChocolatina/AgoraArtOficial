from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.factories.service_factory import get_service_factory
from datetime import datetime

# Crear blueprint
public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    """
    Página de inicio pública
    """
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    categoria_service = service_factory.get_categoria_service()
    usuario_service = service_factory.get_usuario_service()
    
    # Obtener datos para la página de inicio
    obras_recientes = obra_service.get_all(limit=24)
    categorias = categoria_service.get_all()
    
    # Filtrar solo 4 categorías destacadas (Artes plásticas/físicas) para el menú visual
    nombres_destacados = ['Pintura', 'Escultura', 'Fotografía', 'Arte Urbano']
    categorias_destacadas = [c for c in categorias if c.nombre in nombres_destacados]
    
    artistas_destacados = usuario_service.get_artistas_activos(limit=10)

    return render_template('public/home.html', 
                         obras_recientes=obras_recientes,
                         categorias=categorias,
                         categorias_destacadas=categorias_destacadas,
                         artistas_destacados=artistas_destacados)

@public_bp.route('/explorar')
def explorar():
    """
    Página de exploración de obras y artistas
    """
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    categoria_service = service_factory.get_categoria_service()
    
    # Obtener filtros de búsqueda
    categoria_id = request.args.get('categoria', type=int)
    termino = request.args.get('q', '')
    tipo = request.args.get('tipo', 'proyectos')
    filtro = request.args.get('filtro', '')
    page = request.args.get('page', 1, type=int)
    
    # Enrutamiento según el tipo de búsqueda
    if tipo == 'personas':
        return redirect(url_for('public.artistas', q=termino))
    elif tipo == 'productos':
        # Redirigir a la futura vista de marketplace
        return redirect(url_for('public.productos', q=termino, filtro=filtro))
    
    # Búsqueda por defecto (Proyectos/Imágenes -> Obras)
    obras = obra_service.buscar_obras(termino, limit=12)
    
    # Aplicar ordenamiento según el filtro
    if filtro == 'mas_antiguos':
        obras.sort(key=lambda x: x.fecha_publicacion or datetime.min)
    elif filtro == 'mas_recientes':
        obras.sort(key=lambda x: x.fecha_publicacion or datetime.min, reverse=True)
    elif filtro == 'mas_populares':
        # Ordenar por cantidad de favoritos (ya que vistas_count no existe en el modelo actual)
        obras.sort(key=lambda x: len(x.favoritos_usuarios) if hasattr(x, 'favoritos_usuarios') else 0, reverse=True)
        
    categorias = categoria_service.get_all()

    lienzos = []
    if current_user.is_authenticated and current_user.is_cliente():
        lienzos = service_factory.get_moodboard_service().get_by_usuario(
            current_user.id_usuario
        )

    return render_template('public/explorar.html',
                         obras=obras,
                         categorias=categorias,
                         categoria_actual=categoria_id,
                         termino_busqueda=termino,
                         tipo_busqueda=tipo,
                         filtro_actual=filtro,
                         lienzos=lienzos)

@public_bp.route('/artistas')
def artistas():
    """
    Listado de artistas
    """
    service_factory = get_service_factory()
    usuario_service = service_factory.get_usuario_service()
    
    # Obtener filtros
    termino = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    # Obtener artistas
    if termino:
        artistas = usuario_service.buscar_usuarios(termino, rol='artista', limit=12)
    else:
        artistas = usuario_service.get_artistas_activos(limit=12)
        
    total_obras = sum(a.get_obras_count() for a in artistas)
    total_seguidores = sum(a.get_seguidores_count() for a in artistas)
    
    return render_template('public/artistas.html',
                         artistas=artistas,
                         termino_busqueda=termino,
                         total_obras=total_obras,
                         total_seguidores=total_seguidores)

@public_bp.route('/artista/<int:artista_id>')
def perfil_artista(artista_id):
    """
    Perfil público de artista (mismo layout que el panel del artista, solo lectura)
    """
    service_factory = get_service_factory()
    usuario_service = service_factory.get_usuario_service()
    obra_service = service_factory.get_obra_service()
    blog_service = service_factory.get_blog_service()
    producto_service = service_factory.get_producto_service()
    
    artista = usuario_service.get_by_id(artista_id)
    
    if not artista or not artista.is_artista() or not artista.is_active():
        flash('Artista no encontrado', 'error')
        return redirect(url_for('public.artistas'))
    
    obras = obra_service.get_by_artista(artista_id, visible_only=True)
    entradas_blog = blog_service.get_by_artista(artista_id, visible_only=True)
    productos_tienda = producto_service.get_by_artista(artista_id, disponibles_only=False)

    ultima_obra = obras[0] if obras else None
    ultima_entrada = entradas_blog[0] if entradas_blog else None
    ultimo_producto = productos_tienda[0] if productos_tienda else None

    stats = {
        'obras_count': obra_service.get_count_by_artista(artista_id, visible_only=True),
        'productos_count': producto_service.get_count_by_artista(artista_id, disponibles_only=False),
        'seguidores_count': usuario_service.get_seguidores_count(artista_id),
        'blog_count': blog_service.get_count_by_artista(artista_id, visible_only=True),
    }
    
    siguiendo = False
    suscrito_newsletter = False
    if current_user.is_authenticated and current_user.is_cliente():
        siguiendo = usuario_service.esta_siguiendo_artista(current_user.id_usuario, artista_id)
        newsletter_service = service_factory.get_newsletter_service()
        suscrito_newsletter = newsletter_service.esta_suscrito(
            current_user.id_usuario, artista_id
        )

    tab = request.args.get('tab', 'trabajo')
    if tab == 'portafolio':
        tab = 'trabajo'
    if tab not in ('trabajo', 'blog', 'tienda'):
        tab = 'trabajo'

    return render_template('public/perfil_artista.html',
                         artista=artista,
                         obras=obras,
                         entradas_blog=entradas_blog,
                         productos_tienda=productos_tienda,
                         stats=stats,
                         siguiendo=siguiendo,
                         suscrito_newsletter=suscrito_newsletter,
                         ultima_obra=ultima_obra,
                         ultima_entrada=ultima_entrada,
                         ultimo_producto=ultimo_producto,
                         tab=tab)

@public_bp.route('/blog/<int:entrada_id>')
def detalle_entrada_blog(entrada_id):
    """Lectura pública de una entrada de blog."""
    service_factory = get_service_factory()
    blog_service = service_factory.get_blog_service()
    usuario_service = service_factory.get_usuario_service()

    entrada = blog_service.get_by_id(entrada_id)
    if not entrada or not entrada.is_visible():
        flash('Entrada no encontrada', 'error')
        return redirect(url_for('public.explorar'))

    artista = usuario_service.get_by_id(entrada.id_artista)
    if not artista or not artista.is_artista() or not artista.is_active():
        flash('Artista no encontrado', 'error')
        return redirect(url_for('public.artistas'))

    return render_template(
        'public/detalle_entrada_blog.html',
        entrada=entrada,
        artista=artista,
    )

@public_bp.route('/obra/<int:obra_id>')
def detalle_obra(obra_id):
    """
    Detalle de obra específica
    """
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    
    # Obtener obra
    obra = obra_service.get_by_id(obra_id)
    
    if not obra or not obra.is_visible():
        flash('Obra no encontrada', 'error')
        return redirect(url_for('public.explorar'))
    
    # Verificar si es favorito del usuario actual
    es_favorito = False
    if current_user.is_authenticated:
        es_favorito = obra_service.es_favorito(current_user.id_usuario, obra_id)
    
    # Obtener obras relacionadas del mismo artista
    obras_relacionadas = obra_service.get_by_artista(obra.id_artista, visible_only=True, limit=4)
    obras_relacionadas = [o for o in obras_relacionadas if o.id_obra != obra.id_obra][:3]

    from app.utils.obra_galeria import asegurar_galeria_migrada, listar_imagenes_obra
    asegurar_galeria_migrada(obra)
    galeria_imagenes = listar_imagenes_obra(obra)

    lienzos = []
    if current_user.is_authenticated and current_user.is_cliente():
        lienzos = service_factory.get_moodboard_service().get_by_usuario(
            current_user.id_usuario
        )

    producto_service = service_factory.get_producto_service()
    tiene_tienda = producto_service.get_count_by_artista(obra.id_artista, disponibles_only=False) > 0

    return render_template('public/detalle_obra.html',
                         obra=obra,
                         es_favorito=es_favorito,
                         obras_relacionadas=obras_relacionadas,
                         galeria_imagenes=galeria_imagenes,
                         lienzos=lienzos,
                         tiene_tienda=tiene_tienda)

@public_bp.route('/categorias')
def categorias():
    """
    Listado de categorías
    """
    service_factory = get_service_factory()
    categoria_service = service_factory.get_categoria_service()
    
    # Obtener categorías con conteo de obras
    categorias_data = categoria_service.get_all_with_obras_count()
    
    return render_template('public/categorias.html',
                         categorias_data=categorias_data)

@public_bp.route('/categoria/<int:categoria_id>')
def obras_categoria(categoria_id):
    """
    Obras de una categoría específica
    """
    service_factory = get_service_factory()
    categoria_service = service_factory.get_categoria_service()
    obra_service = service_factory.get_obra_service()
    
    # Obtener categoría
    categoria, obras = categoria_service.get_with_obras(categoria_id, limit=12)
    
    if not categoria:
        flash('Categoría no encontrada', 'error')
        return redirect(url_for('public.categorias'))
    
    return render_template('public/obras_categoria.html',
                         categoria=categoria,
                         obras=obras)

@public_bp.route('/acerca-de')
def acerca_de():
    """
    Página sobre la plataforma
    """
    return render_template('public/acerca_de.html')

@public_bp.route('/contacto')
def contacto():
    """
    Página de contacto
    """
    return render_template('public/contacto.html')

def _redirect_back(fallback='public.explorar'):
    return redirect(request.referrer or url_for(fallback))


def _parse_seguir_request():
    if request.is_json:
        data = request.json or {}
        return data.get('artista_id'), data.get('accion')
    return request.form.get('artista_id', type=int), request.form.get('accion')


def _parse_favorito_request():
    if request.is_json:
        data = request.json or {}
        return data.get('obra_id'), data.get('accion')
    return request.form.get('obra_id', type=int), request.form.get('accion')


# API endpoints para AJAX y formularios HTML
@public_bp.route('/api/seguir-artista', methods=['POST'])
@login_required
def seguir_artista():
    """Seguir o dejar de seguir a un artista (JSON o formulario)."""
    if not current_user.is_cliente():
        if request.is_json:
            return jsonify({'error': 'Solo los clientes pueden seguir artistas'}), 403
        flash('Solo los clientes pueden seguir artistas', 'error')
        return _redirect_back('public.artistas')

    artista_id, accion = _parse_seguir_request()
    service_factory = get_service_factory()
    usuario_service = service_factory.get_usuario_service()

    if accion == 'seguir':
        exitoso = usuario_service.seguir_artista(current_user.id_usuario, artista_id)
        mensaje = 'Ahora sigues a este artista' if exitoso else 'Error al seguir artista'
    else:
        exitoso = usuario_service.dejar_de_seguir_artista(current_user.id_usuario, artista_id)
        mensaje = 'Has dejado de seguir a este artista' if exitoso else 'Error al dejar de seguir artista'

    if request.is_json:
        return jsonify({'exitoso': exitoso, 'mensaje': mensaje})

    flash(mensaje, 'success' if exitoso else 'error')
    next_url = request.form.get('next') or request.referrer
    if next_url:
        return redirect(next_url)
    if artista_id:
        return redirect(url_for('public.perfil_artista', artista_id=artista_id))
    return _redirect_back('public.artistas')


@public_bp.route('/api/favorito-obra', methods=['POST'])
@login_required
def favorito_obra():
    """Agregar o quitar obra de favoritos (JSON o formulario)."""
    obra_id, accion = _parse_favorito_request()
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()

    if accion == 'agregar':
        exitoso = obra_service.agregar_favorito(current_user.id_usuario, obra_id)
        mensaje = 'Obra agregada a favoritos' if exitoso else 'Error al agregar a favoritos'
    else:
        exitoso = obra_service.quitar_favorito(current_user.id_usuario, obra_id)
        mensaje = 'Obra quitada de favoritos' if exitoso else 'Error al quitar de favoritos'

    if request.is_json:
        return jsonify({'exitoso': exitoso, 'mensaje': mensaje})

    flash(mensaje, 'success' if exitoso else 'error')
    if obra_id:
        return redirect(url_for('public.detalle_obra', obra_id=obra_id))
    return _redirect_back('cliente.obras_favoritas')


@public_bp.route('/obra/<int:obra_id>/favorito/toggle', methods=['POST'])
@login_required
def toggle_favorito_obra(obra_id):
    """Quitar obra de favoritos desde el listado del cliente."""
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    exitoso = obra_service.quitar_favorito(current_user.id_usuario, obra_id)
    if exitoso:
        flash('Obra quitada de favoritos', 'success')
    else:
        flash('No se pudo quitar de favoritos', 'error')
    return redirect(url_for('cliente.obras_favoritas'))


@public_bp.route('/artista/<int:artista_id>/newsletter', methods=['POST'])
@login_required
def toggle_newsletter_artista(artista_id):
    """Suscribir o cancelar newsletter de un artista."""
    if not current_user.is_cliente():
        flash('Solo los clientes pueden suscribirse al newsletter', 'error')
        return redirect(url_for('public.perfil_artista', artista_id=artista_id))

    accion = request.form.get('accion')
    newsletter_service = get_service_factory().get_newsletter_service()

    if accion == 'desuscribir':
        exitoso = newsletter_service.desuscribir(current_user.id_usuario, artista_id)
        mensaje = 'Te has dado de baja del newsletter' if exitoso else 'Error al cancelar'
    else:
        exitoso = newsletter_service.suscribir(current_user.id_usuario, artista_id)
        mensaje = 'Te suscribiste al newsletter del artista' if exitoso else 'Error al suscribirte'

    flash(mensaje, 'success' if exitoso else 'error')
    return redirect(url_for('public.perfil_artista', artista_id=artista_id))

@public_bp.route('/api/buscar')
def api_buscar():
    """
    API para búsqueda en tiempo real
    """
    termino = request.args.get('q', '')
    tipo = request.args.get('tipo', 'obras')  # 'obras', 'artistas', 'categorias'
    
    service_factory = get_service_factory()
    resultados = []
    
    if tipo == 'obras':
        obra_service = service_factory.get_obra_service()
        obras = obra_service.buscar_obras(termino, limit=5)
        resultados = [{'id': o.id_obra, 'titulo': o.titulo, 'tipo': 'obra'} for o in obras]
    
    elif tipo == 'artistas':
        usuario_service = service_factory.get_usuario_service()
        artistas = usuario_service.buscar_usuarios(termino, rol='artista', limit=5)
        resultados = [{'id': a.id_usuario, 'nombre': a.nombre, 'tipo': 'artista'} for a in artistas]
    
    elif tipo == 'categorias':
        categoria_service = service_factory.get_categoria_service()
        categorias = categoria_service.buscar_categorias(termino, limit=5)
        resultados = [{'id': c.id_categoria, 'nombre': c.nombre, 'tipo': 'categoria'} for c in categorias]
    
    return jsonify({
        'resultados': resultados
    })
@public_bp.route('/productos')
def productos():
    """
    Marketplace - Listado de productos a la venta (Etsy style)
    """
    termino = request.args.get('q', '').strip()
    service_factory = get_service_factory()
    producto_service = service_factory.get_producto_service()

    if termino:
        productos_lista = producto_service.buscar_productos(termino, limit=48)
        productos_lista = [p for p in productos_lista if p.is_disponible()]
    else:
        productos_lista = producto_service.get_disponibles(limit=48)

    return render_template(
        'public/productos.html',
        productos=productos_lista,
        termino_busqueda=termino,
    )


@public_bp.route('/productos/<int:producto_id>')
def detalle_producto(producto_id):
    """Ficha pública de un producto del marketplace."""
    service_factory = get_service_factory()
    producto_service = service_factory.get_producto_service()
    producto = producto_service.get_by_id(producto_id)

    if not producto or not producto.is_disponible():
        flash('Producto no disponible', 'error')
        return redirect(url_for('public.productos'))

    relacionados = []
    if producto.id_artista:
        todos = producto_service.get_by_artista(producto.id_artista, disponibles_only=True)
        relacionados = [p for p in todos if p.id_producto != producto.id_producto][:4]

    return render_template(
        'public/detalle_producto.html',
        producto=producto,
        relacionados=relacionados,
    )
