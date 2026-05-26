"""Formato de precios por moneda (COP, USD, EUR)."""

MONEDA_DEFAULT = 'COP'
MONEDAS_VALIDAS = frozenset({'COP', 'USD', 'EUR'})


def normalizar_moneda(codigo):
    m = (codigo or MONEDA_DEFAULT).strip().upper()
    return m if m in MONEDAS_VALIDAS else MONEDA_DEFAULT


def _entero_miles_puntos(valor):
    """Ej: 56000 -> '56.000'"""
    try:
        n = int(round(float(valor)))
    except (TypeError, ValueError):
        n = 0
    signo = '-' if n < 0 else ''
    s = str(abs(n))
    grupos = []
    while s:
        grupos.append(s[-3:])
        s = s[:-3]
    return signo + '.'.join(reversed(grupos))


def _decimal_miles_puntos(valor, decimales=2):
    """Ej: 128999.99 -> '128.999,99'"""
    try:
        v = float(valor)
    except (TypeError, ValueError):
        v = 0.0
    signo = '-' if v < 0 else ''
    v = abs(v)
    entero = int(v)
    frac = round(v - entero, decimales)
    dec_txt = f'{frac:.{decimales}f}'.split('.')[1] if decimales else ''
    return f'{signo}{_entero_miles_puntos(entero)},{dec_txt}' if decimales else f'{signo}{_entero_miles_puntos(entero)}'


def formatear_precio(precio, moneda=MONEDA_DEFAULT):
    """Devuelve texto legible: $450.000 COP, US$50,00, €50,00, etc."""
    try:
        valor = float(precio)
    except (TypeError, ValueError):
        valor = 0.0
    m = normalizar_moneda(moneda)
    if m == 'EUR':
        return f'€{_decimal_miles_puntos(valor, 2)}'
    if m == 'COP':
        if abs(valor - round(valor)) < 0.005:
            return f'${_entero_miles_puntos(valor)} COP'
        return f'${_decimal_miles_puntos(valor, 2)} COP'
    return f'US${_decimal_miles_puntos(valor, 2)}'


def stripe_currency_code(moneda):
    return normalizar_moneda(moneda).lower()


def stripe_unit_amount(precio, moneda=MONEDA_DEFAULT):
    """Convierte precio a unidad mínima de Stripe (centavos)."""
    try:
        valor = float(precio)
    except (TypeError, ValueError):
        valor = 0.0
    return max(1, int(round(valor * 100)))
