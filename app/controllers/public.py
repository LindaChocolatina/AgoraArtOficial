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
    
    return render_template('public/explorar.html',
                         obras=obras,
                         categorias=categorias,
                         categoria_actual=categoria_id,
                         termino_busqueda=termino,
                         tipo_busqueda=tipo,
                         filtro_actual=filtro)

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
    Perfil público de artista
    """
    service_factory = get_service_factory()
    usuario_service = service_factory.get_usuario_service()
    obra_service = service_factory.get_obra_service()
    
    # Obtener datos del artista
    artista = usuario_service.get_by_id(artista_id)
    
    if not artista or not artista.is_artista() or not artista.is_active():
        flash('Artista no encontrado', 'error')
        return redirect(url_for('public.artistas'))
    
    # Obtener obras del artista
    obras = obra_service.get_by_artista(artista_id, visible_only=True, limit=12)
    
    # Verificar si el usuario actual sigue a este artista
    siguiendo = False
    if current_user.is_authenticated and current_user.is_cliente():
        siguiendo = usuario_service.esta_siguiendo_artista(current_user.id_usuario, artista_id)
    
    # Obtener última obra/entrada/producto para mostrar actividad
    blog_service = service_factory.get_blog_service()
    producto_service = service_factory.get_producto_service()

    ultima_obra = obra_service.get_by_artista(artista_id, visible_only=True, limit=1)
    ultima_obra = ultima_obra[0] if ultima_obra else None
    entradas = blog_service.get_by_artista(artista_id, visible_only=True)
    ultima_entrada = entradas[0] if entradas else None
    productos = producto_service.get_by_artista(artista_id, disponibles_only=False, limit=1)
    ultimo_producto = productos[0] if productos else None

    return render_template('public/perfil_artista.html',
                         artista=artista,
                         obras=obras,
                         siguiendo=siguiendo,
                         ultima_obra=ultima_obra,
                         ultima_entrada=ultima_entrada,
                         ultimo_producto=ultimo_producto)

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

    producto_service = service_factory.get_producto_service()
    productos_artista = producto_service.get_by_artista(obra.id_artista, disponibles_only=False, limit=20)

    from app.utils.obra_galeria import asegurar_galeria_migrada, listar_imagenes_obra
    asegurar_galeria_migrada(obra)
    galeria_imagenes = listar_imagenes_obra(obra)

    return render_template('public/detalle_obra.html',
                         obra=obra,
                         es_favorito=es_favorito,
                         obras_relacionadas=obras_relacionadas,
                         productos_artista=productos_artista,
                         galeria_imagenes=galeria_imagenes)

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

# API endpoints para AJAX
@public_bp.route('/api/seguir-artista', methods=['POST'])
@login_required
def seguir_artista():
    """
    API para seguir/dejar de seguir a un artista
    """
    if not current_user.is_cliente():
        return jsonify({'error': 'Solo los clientes pueden seguir artistas'}), 403
    
    artista_id = request.json.get('artista_id')
    accion = request.json.get('accion')  # 'seguir' o 'dejar_seguir'
    
    service_factory = get_service_factory()
    usuario_service = service_factory.get_usuario_service()
    
    if accion == 'seguir':
        exitoso = usuario_service.seguir_artista(current_user.id_usuario, artista_id)
        mensaje = 'Ahora sigues a este artista' if exitoso else 'Error al seguir artista'
    else:
        exitoso = usuario_service.dejar_de_seguir_artista(current_user.id_usuario, artista_id)
        mensaje = 'Has dejado de seguir a este artista' if exitoso else 'Error al dejar de seguir artista'
    
    return jsonify({
        'exitoso': exitoso,
        'mensaje': mensaje
    })

@public_bp.route('/api/favorito-obra', methods=['POST'])
@login_required
def favorito_obra():
    """
    API para agregar/quitar obra de favoritos
    """
    obra_id = request.json.get('obra_id')
    accion = request.json.get('accion')  # 'agregar' o 'quitar'
    
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    
    if accion == 'agregar':
        exitoso = obra_service.agregar_favorito(current_user.id_usuario, obra_id)
        mensaje = 'Obra agregada a favoritos' if exitoso else 'Error al agregar a favoritos'
    else:
        exitoso = obra_service.quitar_favorito(current_user.id_usuario, obra_id)
        mensaje = 'Obra quitada de favoritos' if exitoso else 'Error al quitar de favoritos'
    
    return jsonify({
        'exitoso': exitoso,
        'mensaje': mensaje
    })

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
