"""Envío de correos (reset de contraseña y similares)."""
from flask import current_app, render_template
from flask_mail import Mail, Message

mail = Mail()


def mail_configurado():
    cfg = current_app.config
    return bool(cfg.get('MAIL_SERVER') and cfg.get('MAIL_USERNAME'))


def modo_demo_correo():
    """Sin SMTP → enlace visible en pantalla (desarrollo)."""
    if current_app.config.get('PASSWORD_RESET_DEMO', False):
        return True
    return current_app.debug and not mail_configurado()


def enviar_correo_reset(destinatario, reset_url):
    asunto = 'Restablecer contraseña — Ágora Art'
    cuerpo_texto = (
        'Recibimos una solicitud para restablecer tu contraseña en Ágora Art.\n\n'
        f'Abre este enlace (válido 1 hora):\n{reset_url}\n\n'
        'Si no solicitaste esto, ignora este mensaje.'
    )
    cuerpo_html = render_template(
        'emails/reset_password.html',
        reset_url=reset_url,
    )
    remitente = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')
    msg = Message(
        subject=asunto,
        recipients=[destinatario],
        body=cuerpo_texto,
        html=cuerpo_html,
        sender=remitente,
    )
    mail.send(msg)
