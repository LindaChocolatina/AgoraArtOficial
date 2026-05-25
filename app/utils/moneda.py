"""Formato de precios por moneda (COP, USD, EUR)."""

MONEDA_DEFAULT = 'COP'
MONEDAS_VALIDAS = frozenset({'COP', 'USD', 'EUR'})


def normalizar_moneda(codigo):
    m = (codigo or MONEDA_DEFAULT).strip().upper()
    return m if m in MONEDAS_VALIDAS else MONEDA_DEFAULT


def formatear_precio(precio, moneda=MONEDA_DEFAULT):
    """Devuelve texto legible: $450.000 COP, US$50.00, €50.00, etc."""
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


def stripe_currency_code(moneda):
    return normalizar_moneda(moneda).lower()


def stripe_unit_amount(precio, moneda=MONEDA_DEFAULT):
    """Convierte precio a unidad mínima de Stripe (centavos)."""
    try:
        valor = float(precio)
    except (TypeError, ValueError):
        valor = 0.0
    return max(1, int(round(valor * 100)))
