"""Integración de pasarela de pago (Stripe) y modo demo local."""

import logging

logger = logging.getLogger(__name__)


class PaymentService:
    """Orquesta el cobro vía Stripe Checkout o simulación en desarrollo."""

    def __init__(self, session, config):
        self.session = session
        self.config = config

    def modo_pago(self):
        if self.config.get('STRIPE_SECRET_KEY'):
            return 'stripe'
        return 'demo'

    def validar_moneda_unica(self, items):
        monedas = set()
        for item in items:
            producto = item['producto']
            moneda = (getattr(producto, 'moneda', None) or 'COP').upper()
            monedas.add(moneda)
        if len(monedas) > 1:
            return False, None, (
                'Tu carrito mezcla monedas distintas. Compra productos de una sola moneda a la vez.'
            )
        return True, (monedas.pop() if monedas else 'COP'), None

    def crear_sesion_stripe(self, orden, items, success_url, cancel_url):
        import stripe

        stripe.api_key = self.config['STRIPE_SECRET_KEY']
        ok, moneda, error = self.validar_moneda_unica(items)
        if not ok:
            return None, error

        from app.utils.moneda import stripe_currency_code, stripe_unit_amount

        line_items = []
        for item in items:
            producto = item['producto']
            imagen = producto.imagen
            product_data = {'name': producto.nombre[:120]}
            if imagen and imagen.startswith('http'):
                product_data['images'] = [imagen]

            line_items.append({
                'price_data': {
                    'currency': stripe_currency_code(moneda),
                    'product_data': product_data,
                    'unit_amount': stripe_unit_amount(producto.precio, moneda),
                },
                'quantity': item['cantidad'],
            })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=str(orden.id_orden),
            metadata={
                'orden_id': str(orden.id_orden),
                'cliente_id': str(orden.id_cliente),
            },
        )
        return checkout_session, None

    def verificar_sesion_stripe(self, session_id):
        import stripe

        stripe.api_key = self.config['STRIPE_SECRET_KEY']
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        if checkout_session.payment_status != 'paid':
            return False, None, 'El pago aún no está confirmado.'
        orden_id = checkout_session.metadata.get('orden_id') or checkout_session.client_reference_id
        if not orden_id:
            return False, None, 'No se pudo vincular el pago con la orden.'
        referencia = checkout_session.payment_intent or checkout_session.id
        cliente_id = checkout_session.metadata.get('cliente_id')
        return True, {
            'orden_id': int(orden_id),
            'cliente_id': int(cliente_id) if cliente_id else None,
            'referencia': str(referencia),
            'monto': float(checkout_session.amount_total or 0) / 100.0,
            'proveedor': 'Stripe',
        }, None

    def referencia_demo(self, orden_id):
        return f'demo-{orden_id}-{int(__import__("time").time())}'
