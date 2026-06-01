from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from app.factories.app_factory import db
from app.factories.service_factory import get_service_factory
from app.utils.perfil_usuario import foto_perfil_desde_form
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


def _cliente_nav(user_id, active_nav=''):
    """Contadores y estado activo para el menú lateral del cliente."""
    service_factory = get_service_factory(db.session)
    usuario_service = service_factory.get_usuario_service()
    obra_service = service_factory.get_obra_service()
    moodboard_service = service_factory.get_moodboard_service()
    orden_service = service_factory.get_orden_service()
    newsletter_service = service_factory.get_newsletter_service()

    return {
        'active_nav': active_nav,
        'nav_counts': {
            'favoritos_count': obra_service.get_favoritos_count(user_id),
            'lienzos_count': moodboard_service.get_count_usuario(user_id),
            'siguiendo_count': usuario_service.get_siguiendo_count(user_id),
            'ordenes_count': orden_service.get_count_by_usuario(user_id),
            'newsletters_count': newsletter_service.count_no_leidos(user_id),
            'suscripciones_count': newsletter_service.count_suscripciones(user_id),
        },
    }


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
        tab = request.args.get('tab', 'lienzos')
        if tab not in ('favoritos', 'lienzos', 'compras', 'siguiendo'):
            tab = 'lienzos'

        service_factory = get_service_factory(db.session)
        usuario_service = service_factory.get_usuario_service()
        obra_service = service_factory.get_obra_service()
        moodboard_service = service_factory.get_moodboard_service()
        orden_service = service_factory.get_orden_service()
        
        stats = {
            'siguiendo_count': usuario_service.get_siguiendo_count(user_id),
            'favoritos_count': obra_service.get_favoritos_count(user_id),
            'lienzos_count': moodboard_service.get_count_usuario(user_id),
            'ordenes_count': orden_service.get_count_by_usuario(user_id)
        }
        
        obras_favoritas = obra_service.get_favoritos_usuario(user_id)
        lienzos = moodboard_service.get_by_usuario(user_id)
        ordenes = orden_service.get_by_usuario(user_id)
        artistas_siguiendo = usuario_service.get_siguiendo(user_id) if tab == 'siguiendo' else []
        
        ctx = _cliente_nav(user_id, active_nav=tab if tab in ('favoritos', 'lienzos', 'compras', 'siguiendo') else 'lienzos')
        
        return render_template('cliente/dashboard.html',
                             tab=tab,
                             stats=stats,
                             obras_favoritas=obras_favoritas,
                             lienzos=lienzos,
                             ordenes=ordenes,
                             artistas_siguiendo=artistas_siguiendo,
                             **ctx)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR CRÍTICO en dashboard de cliente:\n{error_details}")
        flash('Error al cargar el dashboard. Por favor, intenta de nuevo más tarde.', 'error')
        return redirect(url_for('public.home'))

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
        data.update(foto_perfil_desde_form(request, current_app.config['UPLOAD_FOLDER']))
        
        # Validar y actualizar
        service_factory = get_service_factory(db.session)
        usuario_service = service_factory.get_usuario_service()
        
        exitoso, usuario_actualizado = usuario_service.actualizar_usuario(current_user.id_usuario, data)
        
        if exitoso:
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('cliente.dashboard'))
        else:
            flash('Error al actualizar el perfil', 'error')
    
    return render_template('cliente/editar_perfil.html', **_cliente_nav(current_user.id_usuario, active_nav='perfil'))


@cliente_bp.route('/foto-perfil', methods=['GET', 'POST'])
@login_required
@requiere_cliente
def editar_foto_perfil():
    """Subir, cambiar o quitar la foto de perfil del cliente."""
    service_factory = get_service_factory(db.session)
    usuario_service = service_factory.get_usuario_service()

    if request.method == 'POST':
        datos = foto_perfil_desde_form(request, current_app.config['UPLOAD_FOLDER'])
        if not datos:
            flash('Selecciona una imagen o marca quitar la foto actual.', 'error')
        else:
            exitoso, _ = usuario_service.actualizar_usuario(current_user.id_usuario, datos)
            if exitoso:
                flash('Foto de perfil actualizada.', 'success')
                return redirect(url_for('cliente.dashboard'))
            flash('No se pudo guardar la foto.', 'error')

    return render_template(
        'cliente/editar_foto_perfil.html',
        **_cliente_nav(current_user.id_usuario, active_nav='foto'),
    )

@cliente_bp.route('/artistas-siguiendo')
@login_required
@requiere_cliente
def artistas_siguiendo():
    """Redirige al tab Artistas del dashboard."""
    return redirect(url_for('cliente.dashboard', tab='siguiendo'))

@cliente_bp.route('/obras-favoritas')
@login_required
@requiere_cliente
def obras_favoritas():
    """Redirige a la pestaña Favoritos del dashboard."""
    return redirect(url_for('cliente.dashboard', tab='favoritos'))

@cliente_bp.route('/lienzos')
@login_required
@requiere_cliente
def lienzos():
    """Redirige a la pestaña Lienzos del dashboard."""
    return redirect(url_for('cliente.dashboard', tab='lienzos'))

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
            return redirect(url_for('cliente.dashboard', tab='lienzos'))
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
        service_factory = get_service_factory(db.session)
        moodboard_service = service_factory.get_moodboard_service()
        lienzo = moodboard_service.get_by_id(lienzo_id)
        
        if not lienzo or lienzo.id_usuario != current_user.id_usuario:
            flash('Lienzo no encontrado', 'error')
            return redirect(url_for('cliente.dashboard', tab='lienzos'))

        items = moodboard_service.get_items(lienzo_id)
        return render_template('cliente/ver_lienzo.html', lienzo=lienzo, items=items)
    except Exception as e:
        print(f"Error al ver lienzo: {e}")
        flash('Error al cargar el lienzo', 'error')
        return redirect(url_for('cliente.dashboard', tab='lienzos'))


@cliente_bp.route('/lienzos/<int:lienzo_id>/obras/<int:obra_id>/agregar', methods=['POST'])
@login_required
@requiere_cliente
def agregar_obra_lienzo(lienzo_id, obra_id):
    """Guardar una obra en un lienzo del cliente."""
    service_factory = get_service_factory(db.session)
    moodboard_service = service_factory.get_moodboard_service()
    lienzo = moodboard_service.get_by_id(lienzo_id)

    if not lienzo or lienzo.id_usuario != current_user.id_usuario:
        flash('Lienzo no encontrado', 'error')
        return _redirect_back_cliente()

    if moodboard_service.agregar_obra(lienzo_id, obra_id):
        flash(f'Obra guardada en «{lienzo.nombre}»', 'success')
        return redirect(url_for('cliente.ver_lienzo', lienzo_id=lienzo_id))

    flash('No se pudo guardar la obra en el lienzo', 'error')
    return _redirect_back_cliente()


def _redirect_back_cliente():
    ref = request.referrer or ''
    if ref:
        return redirect(ref)
    return redirect(url_for('cliente.dashboard'))


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
    """Historial de compras (pestaña del dashboard)."""
    return redirect(url_for('cliente.dashboard', tab='compras'))


@cliente_bp.route('/ordenes/<int:orden_id>')
@login_required
@requiere_cliente
def ver_orden(orden_id):
    """Detalle de una compra del cliente."""
    service_factory = get_service_factory(db.session)
    orden_service = service_factory.get_orden_service()

    orden = orden_service.get_by_id_for_cliente(orden_id, current_user.id_usuario)
    if not orden:
        flash('Orden no encontrada.', 'error')
        return redirect(url_for('cliente.dashboard', tab='compras'))

    items = list(orden.items.all())
    moneda = 'COP'
    for item in items:
        if item.producto:
            moneda = getattr(item.producto, 'moneda', None) or 'COP'
            break

    pago = orden.pagos.filter_by(estado='aprobado').first() or orden.pagos.first()

    from app.utils.moneda import formatear_precio

    return render_template(
        'cliente/detalle_orden.html',
        orden=orden,
        items=items,
        pago=pago,
        moneda=moneda,
        total_formateado=formatear_precio(orden.total, moneda),
        **_cliente_nav(current_user.id_usuario, active_nav='compras'),
    )

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

    carrito_service.agregar_producto(current_user.id_usuario, producto_id, cantidad)
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
    payment_service = service_factory.get_payment_service()

    items, total = carrito_service.get_items(current_user.id_usuario)
    count = carrito_service.get_count(current_user.id_usuario)
    ok_moneda, moneda, error_moneda = payment_service.validar_moneda_unica(items)

    from app.utils.moneda import formatear_precio

    return render_template(
        'cliente/carrito.html',
        items=items,
        total=total,
        total_formateado=formatear_precio(total, moneda or 'COP'),
        moneda=moneda or 'COP',
        count=count,
        checkout_ok=ok_moneda,
        checkout_error=error_moneda,
        **_cliente_nav(current_user.id_usuario, active_nav='carrito'),
    )

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
        producto_service = service_factory.get_producto_service()

        if cantidad <= 0:
            carrito_service.remover_producto(current_user.id_usuario, producto_id)
            flash('Producto eliminado del carrito', 'success')
        else:
            producto = producto_service.get_by_id(producto_id)
            if producto and cantidad > producto.stock:
                flash(f'Solo hay {producto.stock} unidades disponibles', 'error')
            else:
                carrito_service.actualizar_cantidad(current_user.id_usuario, producto_id, cantidad)
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
    carrito_service.remover_producto(current_user.id_usuario, producto_id)
    flash('Producto eliminado del carrito', 'success')
    
    return redirect(url_for('cliente.carrito'))

@cliente_bp.route('/checkout')
@login_required
@requiere_cliente
def checkout():
    """
    Proceso de pago
    """
    service_factory = get_service_factory(db.session)
    carrito_service = service_factory.get_carrito_service()
    payment_service = service_factory.get_payment_service()

    items, total = carrito_service.get_items(current_user.id_usuario)
    count = carrito_service.get_count(current_user.id_usuario)

    if count == 0:
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('cliente.carrito'))

    ok_moneda, moneda, error_moneda = payment_service.validar_moneda_unica(items)
    if not ok_moneda:
        flash(error_moneda, 'error')
        return redirect(url_for('cliente.carrito'))

    direccion_service = service_factory.get_direccion_service()
    direcciones = direccion_service.get_by_usuario(current_user.id_usuario)

    from app.utils.moneda import formatear_precio

    return render_template(
        'cliente/checkout.html',
        items=items,
        total=total,
        total_formateado=formatear_precio(total, moneda),
        moneda=moneda,
        count=count,
        direcciones=direcciones,
        payment_mode=payment_service.modo_pago(),
        stripe_publishable_key=current_app.config.get('STRIPE_PUBLISHABLE_KEY'),
        **_cliente_nav(current_user.id_usuario, active_nav='carrito'),
    )


@cliente_bp.route('/checkout/procesar', methods=['POST'])
@login_required
@requiere_cliente
def procesar_checkout():
    """
    Crea orden pendiente e inicia el pago (Stripe o modo demo).
    """
    service_factory = get_service_factory(db.session)
    carrito_service = service_factory.get_carrito_service()
    orden_service = service_factory.get_orden_service()
    direccion_service = service_factory.get_direccion_service()
    payment_service = service_factory.get_payment_service()

    items, total = carrito_service.get_items(current_user.id_usuario)
    if not items:
        flash('Tu carrito está vacío', 'error')
        return redirect(url_for('cliente.carrito'))

    ok_moneda, moneda, error_moneda = payment_service.validar_moneda_unica(items)
    if not ok_moneda:
        flash(error_moneda, 'error')
        return redirect(url_for('cliente.carrito'))

    direccion_id, error_dir = _resolver_direccion_checkout(
        direccion_service, current_user.id_usuario, request.form
    )
    if error_dir:
        flash(error_dir, 'error')
        return redirect(url_for('cliente.checkout'))

    exito_orden, orden = orden_service.crear_orden_pendiente(
        cliente_id=current_user.id_usuario,
        direccion_id=direccion_id,
        total=total,
        items=items,
    )
    if not exito_orden or not orden:
        flash('No se pudo preparar tu orden. Revisa stock e intenta de nuevo.', 'error')
        return redirect(url_for('cliente.checkout'))

    if payment_service.modo_pago() == 'stripe':
        success_url = url_for('cliente.checkout_exito', _external=True) + '?session_id={CHECKOUT_SESSION_ID}'
        cancel_url = url_for('cliente.checkout_cancelado', orden_id=orden.id_orden, _external=True)
        session_stripe, error_pago = payment_service.crear_sesion_stripe(
            orden, items, success_url, cancel_url
        )
        if error_pago or not session_stripe:
            orden_service.cancelar_orden(orden.id_orden, current_user.id_usuario)
            flash(error_pago or 'No se pudo iniciar el pago con Stripe.', 'error')
            return redirect(url_for('cliente.checkout'))
        return redirect(session_stripe.url, code=303)

    return redirect(url_for('cliente.checkout_pago_demo', orden_id=orden.id_orden))


@cliente_bp.route('/checkout/pagar/<int:orden_id>', methods=['GET', 'POST'])
@login_required
@requiere_cliente
def checkout_pago_demo(orden_id):
    """Simulación de pasarela para desarrollo y presentaciones sin claves Stripe."""
    service_factory = get_service_factory(db.session)
    orden_service = service_factory.get_orden_service()
    payment_service = service_factory.get_payment_service()
    carrito_service = service_factory.get_carrito_service()

    if payment_service.modo_pago() == 'stripe':
        flash('El pago se procesa con Stripe.', 'info')
        return redirect(url_for('cliente.checkout'))

    orden = orden_service.get_by_id_for_cliente(orden_id, current_user.id_usuario)
    if not orden or orden.estado != 'pendiente':
        flash('Esta orden ya no está disponible para pago.', 'warning')
        return redirect(url_for('cliente.dashboard', tab='compras'))

    if request.method == 'POST':
        referencia = payment_service.referencia_demo(orden.id_orden)
        ok, result = orden_service.confirmar_pago(
            orden.id_orden,
            proveedor='Demo',
            referencia=referencia,
            monto=orden.total,
        )
        if ok:
            carrito_service.vaciar_carrito(current_user.id_usuario)
            flash('¡Pago simulado correctamente! Tu compra quedó registrada.', 'success')
            return redirect(url_for('cliente.checkout_exito', orden_id=orden.id_orden))
        flash(result if isinstance(result, str) else 'No se pudo confirmar el pago.', 'error')
        return redirect(url_for('cliente.checkout_pago_demo', orden_id=orden.id_orden))

    items_orden = []
    for item in orden.items.all():
        items_orden.append({
            'producto': item.producto,
            'cantidad': item.cantidad,
            'subtotal': float(item.subtotal),
        })

    from app.utils.moneda import formatear_precio
    moneda = 'COP'
    if items_orden:
        moneda = getattr(items_orden[0]['producto'], 'moneda', None) or 'COP'

    return render_template(
        'cliente/checkout_pago_demo.html',
        orden=orden,
        items=items_orden,
        total_formateado=formatear_precio(orden.total, moneda),
        **_cliente_nav(current_user.id_usuario, active_nav='carrito'),
    )


@cliente_bp.route('/checkout/exito')
@login_required
@requiere_cliente
def checkout_exito():
    """Retorno tras pago exitoso (Stripe o demo)."""
    service_factory = get_service_factory(db.session)
    orden_service = service_factory.get_orden_service()
    payment_service = service_factory.get_payment_service()
    carrito_service = service_factory.get_carrito_service()

    session_id = request.args.get('session_id')
    orden_id = request.args.get('orden_id', type=int)
    orden = None

    if session_id and payment_service.modo_pago() == 'stripe':
        ok, datos, error = payment_service.verificar_sesion_stripe(session_id)
        if not ok:
            flash(error or 'No se pudo verificar el pago.', 'error')
            return redirect(url_for('cliente.dashboard', tab='compras'))
        if datos.get('cliente_id') and datos['cliente_id'] != current_user.id_usuario:
            flash('Esta orden no te pertenece.', 'error')
            return redirect(url_for('cliente.dashboard', tab='compras'))
        orden = orden_service.get_by_id_for_cliente(datos['orden_id'], current_user.id_usuario)
        if not orden:
            flash('Orden no encontrada.', 'error')
            return redirect(url_for('cliente.dashboard', tab='compras'))
        if orden.estado == 'pendiente':
            ok_pago, result = orden_service.confirmar_pago(
                orden.id_orden,
                proveedor=datos['proveedor'],
                referencia=datos['referencia'],
                monto=datos['monto'],
            )
            if not ok_pago:
                flash(result if isinstance(result, str) else 'Error al confirmar el pago.', 'error')
                return redirect(url_for('cliente.dashboard', tab='compras'))
        carrito_service.vaciar_carrito(current_user.id_usuario)
        flash('¡Pago recibido! Gracias por tu compra.', 'success')
        return render_template(
            'cliente/checkout_exito.html',
            orden=orden,
            **_cliente_nav(current_user.id_usuario, active_nav='compras'),
        )

    if orden_id:
        orden = orden_service.get_by_id_for_cliente(orden_id, current_user.id_usuario)
        if orden and orden.estado == 'pagada':
            return render_template(
                'cliente/checkout_exito.html',
                orden=orden,
                **_cliente_nav(current_user.id_usuario, active_nav='compras'),
            )

    flash('No encontramos el comprobante de tu pago.', 'warning')
    return redirect(url_for('cliente.dashboard', tab='compras'))


@cliente_bp.route('/checkout/cancelado/<int:orden_id>')
@login_required
@requiere_cliente
def checkout_cancelado(orden_id):
    """Usuario canceló el pago en Stripe."""
    service_factory = get_service_factory(db.session)
    orden_service = service_factory.get_orden_service()
    orden_service.cancelar_orden(orden_id, current_user.id_usuario)
    flash('Pago cancelado. Tu carrito sigue disponible.', 'info')
    return redirect(url_for('cliente.carrito'))


@cliente_bp.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Webhook opcional de Stripe para confirmar pagos en producción."""
    from app.factories.app_factory import csrf
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')

    if not webhook_secret or not current_app.config.get('STRIPE_SECRET_KEY'):
        return jsonify({'error': 'Webhook no configurado'}), 400

    import stripe
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return jsonify({'error': 'Payload inválido'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Firma inválida'}), 400

    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        if session_obj.get('payment_status') == 'paid':
            orden_id = session_obj.get('metadata', {}).get('orden_id') or session_obj.get('client_reference_id')
            if orden_id:
                service_factory = get_service_factory(db.session)
                orden_service = service_factory.get_orden_service()
                referencia = session_obj.get('payment_intent') or session_obj.get('id')
                monto = float(session_obj.get('amount_total') or 0) / 100.0
                orden_service.confirmar_pago(int(orden_id), 'Stripe', str(referencia), monto)

    return jsonify({'status': 'ok'})


# Exentar webhook de CSRF (se registra al importar el módulo)
from app.factories.app_factory import csrf
csrf.exempt(stripe_webhook)

@cliente_bp.route('/newsletters')
@login_required
@requiere_cliente
def newsletters():
    """
    Newsletters recibidos (bandeja de entrada)
    """
    try:
        service_factory = get_service_factory(db.session)
        newsletter_service = service_factory.get_newsletter_service()
        inbox = newsletter_service.get_inbox(current_user.id_usuario)
        ctx = _cliente_nav(current_user.id_usuario, active_nav='inbox')
        return render_template('cliente/newsletters.html', inbox=inbox, **ctx)
    except Exception as e:
        print(f"Error al cargar newsletters: {e}")
        flash('Error al cargar tus newsletters', 'error')
        return redirect(url_for('cliente.dashboard'))


@cliente_bp.route('/newsletters/<int:newsletter_id>')
@login_required
@requiere_cliente
def newsletter_detalle(newsletter_id):
    """Ver un newsletter y marcarlo como leído."""
    service_factory = get_service_factory(db.session)
    newsletter_service = service_factory.get_newsletter_service()
    row = newsletter_service.get_para_cliente(current_user.id_usuario, newsletter_id)
    if not row:
        flash('Newsletter no encontrado', 'error')
        return redirect(url_for('cliente.newsletters'))

    news, leido = row
    if not leido:
        newsletter_service.marcar_leido(current_user.id_usuario, newsletter_id)

    ctx = _cliente_nav(current_user.id_usuario, active_nav='inbox')
    return render_template('cliente/newsletter_detalle.html', news=news, **ctx)


@cliente_bp.route('/suscripciones-newsletter')
@login_required
@requiere_cliente
def suscripciones_newsletter():
    """Artistas a cuyo newsletter está suscrito el cliente."""
    service_factory = get_service_factory(db.session)
    newsletter_service = service_factory.get_newsletter_service()
    artistas = newsletter_service.get_artistas_suscritos(current_user.id_usuario)
    ctx = _cliente_nav(current_user.id_usuario, active_nav='suscripciones')
    return render_template('cliente/suscripciones_newsletter.html', artistas=artistas, **ctx)

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
    exitoso = carrito_service.agregar_producto(current_user.id_usuario, producto_id, cantidad)
    
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
    exitoso = carrito_service.remover_producto(current_user.id_usuario, producto_id)
    
    return jsonify({
        'exitoso': exitoso,
        'mensaje': 'Producto quitado del carrito' if exitoso else 'Error al quitar'
    })
