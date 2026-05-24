"""Formato de precios por moneda (USD, EUR, COP)."""

MONEDAS_VALIDAS = frozenset({'USD', 'EUR', 'COP'})


def normalizar_moneda(codigo):
    m = (codigo or 'USD').strip().upper()
    return m if m in MONEDAS_VALIDAS else 'USD'


def formatear_precio(precio, moneda='USD'):
    """Devuelve texto legible: 450.00 USD, 50.00 EUR, etc."""
    try:
        valor = float(precio)
    except (TypeError, ValueError):
        valor = 0.0
    m = normalizar_moneda(moneda)
    if m == 'EUR':
        return f'€{valor:,.2f}'
    if m == 'COP':
        return f'${valor:,.0f} COP'
    return f'US${valor:,.2f}'
