from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.factories.service_factory import get_service_factory
from app.utils.perfil_usuario import foto_perfil_desde_form

# Crear blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de inicio de sesión
    """
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        from app.utils.login_security import obtener_ip_cliente
        ip_address = obtener_ip_cliente()
        
        # Obtener servicio de autenticación
        service_factory = get_service_factory()
        auth_service = service_factory.get_auth_service()
        
        # Intentar login
        exitoso, usuario, mensaje_error = auth_service.login_usuario(
            email, password, remember, ip_address=ip_address,
        )
        
        if exitoso:
            carrito_service = service_factory.get_carrito_service()
            carrito_service.fusionar_sesion(usuario.id_usuario)

            # Redirigir según rol
            if usuario.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif usuario.is_artista():
                return redirect(url_for('artista.dashboard'))
            else:
                return redirect(url_for('cliente.dashboard'))
        else:
            flash(mensaje_error, 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Página de registro de usuarios
    """
    rol_preseleccionado = request.args.get('rol', '')
    if rol_preseleccionado not in ('cliente', 'artista'):
        rol_preseleccionado = ''

    if current_user.is_authenticated:
        return redirect(url_for('public.home'))
    
    if request.method == 'POST':
        # Obtener datos del formulario
        data = {
            'nombre': request.form.get('nombre'),
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'rol': request.form.get('rol', 'cliente'),
            'biografia': request.form.get('biografia', '')
        }
        if data['rol'] not in ('cliente', 'artista'):
            data['rol'] = 'cliente'
        
        # Obtener servicio de autenticación
        service_factory = get_service_factory()
        auth_service = service_factory.get_auth_service()
        
        # Intentar registro
        exitoso, usuario, errores = auth_service.registrar_usuario(data)
        
        if exitoso:
            flash('¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        else:
            for error in errores:
                flash(error, 'error')
    
    return render_template('auth/register.html', rol_preseleccionado=rol_preseleccionado)

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Cerrar sesión
    """
    service_factory = get_service_factory()
    auth_service = service_factory.get_auth_service()
    
    if auth_service.logout_usuario():
        flash('Has cerrado sesión correctamente.', 'info')
    
    return redirect(url_for('public.home'))

@auth_bp.route('/perfil')
@login_required
def perfil():
    """
    Ver perfil de usuario actual
    """
    return render_template('auth/perfil.html')

@auth_bp.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """
    Editar perfil de usuario
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
        
        # Validar datos
        service_factory = get_service_factory()
        auth_service = service_factory.get_auth_service()
        
        errores = []
        
        # Validaciones básicas
        if not data.get('nombre', '').strip():
            errores.append('El nombre es obligatorio')
        
        if not data.get('username', '').strip():
            errores.append('El username es obligatorio')
        elif len(data['username']) < 3:
            errores.append('El username debe tener al menos 3 caracteres')
        elif auth_service.validar_username_duplicado(data['username'], current_user.id_usuario):
            errores.append('El username ya está registrado')
        
        if not data.get('email', '').strip():
            errores.append('El email es obligatorio')
        elif '@' not in data['email'] or '.' not in data['email']:
            errores.append('El email no es válido')
        elif auth_service.validar_email_duplicado(data['email'], current_user.id_usuario):
            errores.append('El email ya está registrado')
        
        if not errores:
            # Actualizar usuario
            usuario_service = service_factory.get_usuario_service()
            exitoso, usuario_actualizado = usuario_service.actualizar_usuario(current_user.id_usuario, data)
            
            if exitoso:
                flash('Perfil actualizado correctamente.', 'success')
                return redirect(url_for('auth.perfil'))
            else:
                flash('Error al actualizar el perfil.', 'error')
        else:
            for error in errores:
                flash(error, 'error')
    
    return render_template('auth/editar_perfil.html')

@auth_bp.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """
    Cambiar contraseña del usuario
    """
    if request.method == 'POST':
        password_actual = request.form.get('password_actual')
        password_nueva = request.form.get('password_nueva')
        password_confirmar = request.form.get('password_confirmar')
        
        errores = []
        
        if not password_actual:
            errores.append('La contraseña actual es obligatoria')
        
        if not password_nueva:
            errores.append('La nueva contraseña es obligatoria')
        elif len(password_nueva) < 6:
            errores.append('La nueva contraseña debe tener al menos 6 caracteres')
        
        if password_nueva != password_confirmar:
            errores.append('Las contraseñas nuevas no coinciden')
        
        if not errores:
            service_factory = get_service_factory()
            auth_service = service_factory.get_auth_service()
            
            exitoso, mensaje = auth_service.cambiar_password(
                current_user.id_usuario, 
                password_actual, 
                password_nueva
            )
            
            if exitoso:
                flash(mensaje, 'success')
                return redirect(url_for('auth.perfil'))
            else:
                flash(mensaje, 'error')
        else:
            for error in errores:
                flash(error, 'error')
    
    return render_template('auth/cambiar_password.html')

@auth_bp.route('/olvide-contrasena', methods=['GET', 'POST'])
def olvide_contrasena():
    """Solicitar enlace para restablecer contraseña."""
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))

    reset_link = None
    if request.method == 'POST':
        email = request.form.get('email', '')
        from app.utils.login_security import obtener_ip_cliente
        ip_address = obtener_ip_cliente()
        service_factory = get_service_factory()
        auth_service = service_factory.get_auth_service()

        def build_url(token):
            return url_for('auth.restablecer_contrasena', token=token, _external=True)

        mensaje, reset_link = auth_service.solicitar_restablecimiento(
            email, build_url, ip_address=ip_address,
        )
        from app.utils.email_envio import modo_demo_correo
        if reset_link and modo_demo_correo():
            flash(
                'Modo local: no se envió ningún correo. Copia el enlace que aparece abajo en esta misma página.',
                'warning',
            )
        else:
            flash(mensaje, 'success')

    from app.utils.email_envio import modo_demo_correo, mail_configurado
    return render_template(
        'auth/olvide_contrasena.html',
        reset_link=reset_link,
        modo_demo=modo_demo_correo(),
        mail_configurado=mail_configurado(),
    )


@auth_bp.route('/restablecer-contrasena/<token>', methods=['GET', 'POST'])
def restablecer_contrasena(token):
    """Nueva contraseña con token de recuperación."""
    if current_user.is_authenticated:
        return redirect(url_for('public.home'))

    if request.method == 'POST':
        password_nueva = request.form.get('password_nueva', '')
        password_confirmar = request.form.get('password_confirmar', '')

        if password_nueva != password_confirmar:
            flash('Las contraseñas no coinciden', 'error')
        elif len(password_nueva) < 6:
            flash('La contraseña debe tener al menos 6 caracteres', 'error')
        else:
            service_factory = get_service_factory()
            auth_service = service_factory.get_auth_service()
            exitoso, mensaje = auth_service.restablecer_password_con_token(
                token,
                password_nueva,
                current_app.config['SECRET_KEY'],
            )
            if exitoso:
                flash(mensaje, 'success')
                return redirect(url_for('auth.login'))
            flash(mensaje, 'error')

    return render_template('auth/restablecer_contrasena.html', token=token)

# API endpoints para AJAX
@auth_bp.route('/api/verificar-email', methods=['POST'])
def verificar_email():
    """
    API para verificar si email ya existe
    """
    email = request.json.get('email')
    exclude_id = request.json.get('exclude_id')
    
    service_factory = get_service_factory()
    auth_service = service_factory.get_auth_service()
    
    existe = auth_service.validar_email_duplicado(email, exclude_id)
    
    return jsonify({
        'existe': existe,
        'mensaje': 'El email ya está registrado' if existe else 'Email disponible'
    })

@auth_bp.route('/api/verificar-username', methods=['POST'])
def verificar_username():
    """
    API para verificar si username ya existe
    """
    username = request.json.get('username')
    exclude_id = request.json.get('exclude_id')
    
    service_factory = get_service_factory()
    auth_service = service_factory.get_auth_service()
    
    existe = auth_service.validar_username_duplicado(username, exclude_id)
    
    return jsonify({
        'existe': existe,
        'mensaje': 'El username ya está registrado' if existe else 'Username disponible'
    })
