from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.factories.service_factory import get_service_factory
from functools import wraps

# Crear blueprint
cliente_bp = Blueprint('cliente', __name__)

def requiere_cliente(f):
    """Decorador para requerir rol de cliente"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_cliente():
            flash('Esta página es solo para clientes', 'error')
            return redirect(url_for('public.home'))
        return f(*args, **kwargs)
    return decorated_function

from app.factories.app_factory import db


def _validar_campos_direccion(data):
    """Validar campos obligatorios de una dirección de envío."""
    errores = []
    for campo in ('nombre_receptor', 'direccion', 'ciudad', 'pais'):
        if not (data.get(campo) or '').strip():
            errores.append(f'El campo {campo} es obligatorio')
    return errores


def _resolver_direccion_checkout(direccion_service, usuario_id, form):
    """
    Obtener id_direccion desde selección o crear una nueva.
    Retorna (id_direccion, error_mensaje).
    """
    direccion_id = form.get('id_direccion', '').strip()

    if direccion_id:
        try:
            direccion_id = int(direccion_id)
        except (TypeError, ValueError):
            return None, 'La dirección seleccionada no es válida'

        direccion = direccion_service.get_by_id_for_usuario(direccion_id, usuario_id)
        if not direccion:
            return None, 'La dirección seleccionada no te pertenece'
        return direccion_id, None

    nueva_dir_data = {
        'id_usuario': usuario_id,
        'nombre_receptor': form.get('nombre_receptor'),
        'direccion': form.get('direccion'),
        'ciudad': form.get('ciudad'),
        'pais': form.get('pais'),
        'codigo_postal': form.get('codigo_postal'),
        'telefono': form.get('telefono'),
    }
    errores = _validar_campos_direccion(nueva_dir_data)
    if errores:
        return None, errores[0]

    exito_dir, nueva_dir = direccion_service.agregar_direccion(nueva_dir_data)
    if exito_dir:
        return nueva_dir.id_direccion, None
    return None, 'Error al guardar la dirección de envío'

@cliente_bp.route('/dashboard')
@login_required
@requiere_cliente
def dashboard():
    """
    Dashboard del cliente
    """
    try:
        user_id = current_user.get_id()
        if not user_id:
            flash('Sesión no válida. Por favor inicia sesión de nuevo.', 'warning')
            return redirect(url_for('auth.login'))
            
        user_id = int(user_id)
        service_factory = get_service_factory(db.session)
        usuario_service = service_factory.get_usuario_service()
        obra_service = service_factory.get_obra_service()
        moodboard_service = service_factory.get_moodboard_service()
        orden_service = service_factory.get_orden_service()
        newsletter_service = service_factory.get_newsletter_service()
        
        # Obtener datos del dashboard
        stats = {
            'siguiendo_count': usuario_service.get_siguiendo_count(user_id),
            'favoritos_count': obra_service.get_favoritos_count(user_id),
            'lienzos_count': moodboard_service.get_count_usuario(user_id),
            'ordenes_count': orden_service.get_count_by_usuario(user_id)
        }
        
        # Obtener artistas que sigue
        artistas_siguiendo = usuario_service.get_siguiendo(user_id, limit=6)
        
        # Obtener obras favoritas
        obras_favoritas = obra_service.get_favoritos_usuario(user_id, limit=6)
        
        # Obtener lienzos (moodboards) para visualización
        lienzos = moodboard_service.get_by_usuario(user_id)
        
        # Obtener newsletters recientes
        newsletters_recientes = []
        try:
            newsletters_recientes = newsletter_service.get_by_usuario(user_id, limit=3)
        except Exception as ns_err:
            print(f"Error al obtener newsletters: {ns_err}")
        
        return render_template('cliente/dashboard.html',
                             stats=stats,
                             artistas_siguiendo=artistas_siguiendo,
                             obras_favoritas=obras_favoritas,
                             lienzos=lienzos,
                             newsletters=newsletters_recientes)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR CRÍTICO en dashboard de cliente:\n{error_details}")
        flash('Error al cargar el dashboard. Por favor, intenta de nuevo más tarde.', 'error')
        return redirect(url_for('public.home'))
    finally:
        try:
            db.session.remove()
        except:
            pass

@cliente_bp.route('/perfil')
@login_required
@requiere_cliente
def perfil():
    """
    Perfil del cliente
    """
    return render_template('cliente/perfil.html')

@cliente_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
@requiere_cliente
def editar_perfil():
    """
    Editar perfil del cliente
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
            return redirect(url_for('cliente.perfil'))
        else:
            flash('Error al actualizar el perfil', 'error')
    
    return render_template('cliente/editar_perfil.html')

@cliente_bp.route('/artistas-siguiendo')
@login_required
@requiere_cliente
def artistas_siguiendo():
    """
    Listado de artistas que sigue el cliente
    """
    service_factory = get_service_factory()
    usuario_service = service_factory.get_usuario_service()
    
    # Obtener artistas que sigue
    artistas = usuario_service.get_siguiendo(current_user.id_usuario)
    
    return render_template('cliente/artistas_siguiendo.html', artistas=artistas)

@cliente_bp.route('/obras-favoritas')
@login_required
@requiere_cliente
def obras_favoritas():
    """
    Listado de obras favoritas del cliente
    """
    service_factory = get_service_factory()
    obra_service = service_factory.get_obra_service()
    
    # Obtener obras favoritas
    obras = obra_service.get_favoritos_usuario(current_user.id_usuario)
    
    return render_template('cliente/obras_favoritas.html', obras=obras)

@cliente_bp.route('/lienzos')
@login_required
@requiere_cliente
def lienzos():
    """
    Moodboards del cliente
    """
    try:
        service_factory = get_service_factory()
        moodboard_service = service_factory.get_moodboard_service()
        lienzos = moodboard_service.get_by_usuario(current_user.id_usuario)
        return render_template('cliente/lienzos.html', lienzos=lienzos)
    except Exception as e:
        print(f"Error al cargar lienzos: {e}")
        flash('Error al cargar tus lienzos', 'error')
        return redirect(url_for('cliente.dashboard'))

@cliente_bp.route('/lienzos/nuevo', methods=['GET', 'POST'])
@login_required
@requiere_cliente
def nuevo_lienzo():
    """
    Crear nuevo moodboard
    """
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        
        if not nombre.strip():
            flash('El nombre del lienzo es obligatorio', 'error')
            return render_template('cliente/nuevo_lienzo.html')
        
        service_factory = get_service_factory()
        moodboard_service = service_factory.get_moodboard_service()
        exito, lienzo = moodboard_service.crear_lienzo(current_user.id_usuario, nombre)
        
        if exito:
            flash('Lienzo creado correctamente', 'success')
            return redirect(url_for('cliente.lienzos'))
        else:
            flash('Error al crear el lienzo', 'error')
            
    return render_template('cliente/nuevo_lienzo.html')

@cliente_bp.route('/lienzos/<int:lienzo_id>')
@login_required
@requiere_cliente
def ver_lienzo(lienzo_id):
    """
    Ver detalles de un lienzo (moodboard)
    """
    try:
        service_factory = get_service_factory()
        moodboard_service = service_factory.get_moodboard_service()
        lienzo = moodboard_service.get_by_id(lienzo_id)
        
        if not lienzo or lienzo.id_usuario != current_user.id_usuario:
            flash('Lienzo no encontrado', 'error')
            return redirect(url_for('cliente.lienzos'))
            
        return render_template('cliente/ver_lienzo.html', lienzo=lienzo)
    except Exception as e:
        print(f"Error al ver lienzo: {e}")
        flash('Error al cargar el lienzo', 'error')
        return redirect(url_for('cliente.lienzos'))

@cliente_bp.route('/direcciones')
@login_required
@requiere_cliente
def direcciones():
    """
    Direcciones de envío del cliente
    """
    try:
        service_factory = get_service_factory()
        direccion_service = service_factory.get_direccion_service()
        direcciones = direccion_service.get_by_usuario(current_user.id_usuario)
        return render_template('cliente/direcciones.html', direcciones=direcciones)
    except Exception as e:
        print(f"Error al cargar direcciones: {e}")
        flash('Error al cargar tus direcciones', 'error')
        return redirect(url_for('cliente.dashboard'))

@cliente_bp.route('/direcciones/nueva', methods=['GET', 'POST'])
@login_required
@requiere_cliente
def nueva_direccion():
    """
    Agregar nueva dirección
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        data = {
            'id_usuario': current_user.id_usuario,
            'nombre_receptor': request.form.get('nombre_receptor'),
            'direccion': request.form.get('direccion'),
            'ciudad': request.form.get('ciudad'),
            'pais': request.form.get('pais'),
            'codigo_postal': request.form.get('codigo_postal'),
            'telefono': request.form.get('telefono')
        }
        
        errores = _validar_campos_direccion(data)

        if not errores:
            service_factory = get_service_factory()
            direccion_service = service_factory.get_direccion_service()
            exito, direccion = direccion_service.agregar_direccion(data)

            if exito:
                flash('Dirección agregada correctamente', 'success')
                if request.args.get('next') == 'checkout':
                    return redirect(url_for('cliente.checkout'))
                return redirect(url_for('cliente.direcciones'))
            flash('Error al agregar la dirección', 'error')
        else:
            for error in errores:
                flash(error, 'error')

    return render_template('cliente/nueva_direccion.html', volver_checkout=request.args.get('next') == 'checkout')


@cliente_bp.route('/direcciones/<int:direccion_id>/editar', methods=['GET', 'POST'])
@login_required
@requiere_cliente
def editar_direccion(direccion_id):
    """Editar una dirección de envío (no permitido si tiene órdenes)"""
    service_factory = get_service_factory()
    direccion_service = service_factory.get_direccion_service()
    direccion = direccion_service.get_by_id_for_usuario(direccion_id, current_user.id_usuario)

    if not direccion:
        flash('Dirección no encontrada', 'error')
        return redirect(url_for('cliente.direcciones'))

    if direccion.tiene_ordenes_asociadas():
        flash('No puedes editar una dirección usada en una compra anterior', 'error')
        return redirect(url_for('cliente.direcciones'))

    if request.method == 'POST':
        data = {
            'nombre_receptor': request.form.get('nombre_receptor'),
            'direccion': request.form.get('direccion'),
            'ciudad': request.form.get('ciudad'),
            'pais': request.form.get('pais'),
            'codigo_postal': request.form.get('codigo_postal'),
            'telefono': request.form.get('telefono'),
        }
        errores = _validar_campos_direccion(data)
        if errores:
            for error in errores:
                flash(error, 'error')
        else:
            exito, _, motivo = direccion_service.actualizar_direccion(
                direccion_id, current_user.id_usuario, data
            )
            if exito:
                flash('Dirección actualizada correctamente', 'success')
                return redirect(url_for('cliente.direcciones'))
            if motivo == 'tiene_ordenes':
                flash('No puedes editar una dirección usada en una compra anterior', 'error')
            else:
                flash('Error al actualizar la dirección', 'error')

    return render_template('cliente/editar_direccion.html', direccion=direccion)


@cliente_bp.route('/direcciones/<int:direccion_id>/eliminar', methods=['POST'])
@login_required
@requiere_cliente
def eliminar_direccion(direccion_id):
    """Eliminar una dirección sin órdenes asociadas"""
    service_factory = get_service_factory()
    direccion_service = service_factory.get_direccion_service()
    exito, motivo = direccion_service.eliminar_direccion(direccion_id, current_user.id_usuario)

    if exito:
        flash('Dirección eliminada correctamente', 'success')
    elif motivo == 'tiene_ordenes':
        flash('No puedes eliminar una dirección usada en una compra anterior', 'error')
    elif motivo == 'no_encontrada':
        flash('Dirección no encontrada', 'error')
    else:
        flash('Error al eliminar la dirección', 'error')

    return redirect(url_for('cliente.direcciones'))

@cliente_bp.route('/ordenes')
@login_required
@requiere_cliente
def ordenes():
    """
    Historial de órdenes del cliente
    """
    try:
        service_factory = get_service_factory()
        orden_service = service_factory.get_orden_service()
        ordenes = orden_service.get_by_usuario(current_user.id_usuario)
        return render_template('cliente/ordenes.html', ordenes=ordenes)
    except Exception as e:
        print(f"Error al cargar órdenes: {e}")
        flash('Error al cargar tus órdenes', 'error')
        return redirect(url_for('cliente.dashboard'))

@cliente_bp.route('/carrito/agregar/<int:producto_id>', methods=['POST'])
@login_required
@requiere_cliente
def agregar_al_carrito(producto_id):
    """Agregar un producto al carrito desde el marketplace (formulario HTML)."""
    service_factory = get_service_factory()
    producto_service = service_factory.get_producto_service()
    carrito_service = service_factory.get_carrito_service()

    producto = producto_service.get_by_id(producto_id)
    if not producto or not producto.is_disponible():
        flash('Este producto no está disponible', 'error')
        return redirect(request.referrer or url_for('public.productos'))

    cantidad = request.form.get('cantidad', 1, type=int)
    if cantidad < 1:
        cantidad = 1

    carrito_service.agregar_producto(producto_id, cantidad)
    flash(f'"{producto.nombre}" se agregó al carrito', 'success')

    destino = request.form.get('next') or request.referrer or url_for('cliente.carrito')
    return redirect(destino)


@cliente_bp.route('/carrito')
@login_required
@requiere_cliente
def carrito():
    """
    Carrito de compras
    """
    service_factory = get_service_factory()
    carrito_service = service_factory.get_carrito_service()
    
    items, total = carrito_service.get_items()
    count = carrito_service.get_count()
    
    return render_template('cliente/carrito.html', items=items, total=total, count=count)

@cliente_bp.route('/carrito/actualizar/<int:producto_id>', methods=['POST'])
@login_required
@requiere_cliente
def actualizar_carrito(producto_id):
    """
    Actualizar cantidad de un producto en el carrito
    """
    cantidad = request.form.get('cantidad', type=int)
    
    if cantidad is not None:
        service_factory = get_service_factory()
        carrito_service = service_factory.get_carrito_service()
        carrito_service.actualizar_cantidad(producto_id, cantidad)
        flash('Carrito actualizado', 'success')
        
    return redirect(url_for('cliente.carrito'))

@cliente_bp.route('/carrito/remover/<int:producto_id>', methods=['POST'])
@login_required
@requiere_cliente
def remover_carrito(producto_id):
    """
    Remover producto del carrito
    """
    service_factory = get_service_factory()
    carrito_service = service_factory.get_carrito_service()
    carrito_service.remover_producto(producto_id)
    flash('Producto eliminado del carrito', 'success')
    
    return redirect(url_for('cliente.carrito'))

@cliente_bp.route('/checkout')
@login_required
@requiere_cliente
def checkout():
    """
    Proceso de pago
    """
    service_factory = get_service_factory()
    carrito_service = service_factory.get_carrito_service()
    
    items, total = carrito_service.get_items()
    count = carrito_service.get_count()
    
    if count == 0:
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('cliente.carrito'))

    direccion_service = service_factory.get_direccion_service()
    direcciones = direccion_service.get_by_usuario(current_user.id_usuario)

    return render_template(
        'cliente/checkout.html',
        items=items,
        total=total,
        count=count,
        direcciones=direcciones,
    )

@cliente_bp.route('/checkout/procesar', methods=['POST'])
@login_required
@requiere_cliente
def procesar_checkout():
    """
    Procesar pago de la orden y crear el registro en la base de datos
    """
    service_factory = get_service_factory()
    carrito_service = service_factory.get_carrito_service()
    orden_service = service_factory.get_orden_service()
    direccion_service = service_factory.get_direccion_service()
    
    # 1. Validar carrito
    items, total = carrito_service.get_items()
    if not items:
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('cliente.carrito'))
        
    # 2. Obtener o crear dirección de envío
    direccion_id, error_dir = _resolver_direccion_checkout(
        direccion_service, current_user.id_usuario, request.form
    )
    if error_dir:
        flash(error_dir, 'error')
        return redirect(url_for('cliente.checkout'))

    # 3. Crear la orden real
    # Aquí se integraría la pasarela de pagos (Stripe/PayPal)
    # Si el pago es exitoso, procedemos a crear la orden en la DB
    
    exito_orden, orden = orden_service.crear_orden(
        cliente_id=current_user.id_usuario,
        direccion_id=direccion_id,
        total=total,
        items=items
    )
    
    if exito_orden:
        # 4. Vaciar carrito si la orden fue exitosa
        carrito_service.vaciar_carrito()
        flash('¡Compra realizada con éxito! Tu orden está siendo procesada.', 'success')
        return redirect(url_for('cliente.ordenes'))
    else:
        flash('Hubo un problema al procesar tu orden. Por favor intenta de nuevo.', 'error')
        return redirect(url_for('cliente.checkout'))

@cliente_bp.route('/newsletters')
@login_required
@requiere_cliente
def newsletters():
    """
    Newsletters recibidos (bandeja de entrada)
    """
    try:
        service_factory = get_service_factory()
        newsletter_service = service_factory.get_newsletter_service()
        
        # Obtener newsletters del usuario
        newsletters = newsletter_service.get_by_usuario(current_user.id_usuario)
        
        return render_template('cliente/newsletters.html', newsletters=newsletters)
    except Exception as e:
        print(f"Error al cargar newsletters: {e}")
        flash('Error al cargar tus newsletters', 'error')
        return redirect(url_for('cliente.dashboard'))

# API endpoints
@cliente_bp.route('/api/seguir-artista', methods=['POST'])
@login_required
@requiere_cliente
def seguir_artista():
    """
    API para seguir/dejar de seguir a un artista
    """
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

@cliente_bp.route('/api/favorito-obra', methods=['POST'])
@login_required
@requiere_cliente
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

@cliente_bp.route('/api/carrito/agregar', methods=['POST'])
@login_required
@requiere_cliente
def agregar_carrito():
    """
    API para agregar producto al carrito
    """
    producto_id = request.json.get('producto_id')
    cantidad = request.json.get('cantidad', 1)
    
    service_factory = get_service_factory()
    carrito_service = service_factory.get_carrito_service()
    exitoso = carrito_service.agregar_producto(producto_id, cantidad)
    
    return jsonify({
        'exitoso': exitoso,
        'mensaje': 'Producto agregado al carrito' if exitoso else 'Error al agregar'
    })

@cliente_bp.route('/api/carrito/quitar', methods=['POST'])
@login_required
@requiere_cliente
def quitar_carrito():
    """
    API para quitar producto del carrito
    """
    producto_id = request.json.get('producto_id')
    
    service_factory = get_service_factory()
    carrito_service = service_factory.get_carrito_service()
    exitoso = carrito_service.remover_producto(producto_id)
    
    return jsonify({
        'exitoso': exitoso,
        'mensaje': 'Producto quitado del carrito' if exitoso else 'Error al quitar'
    })
