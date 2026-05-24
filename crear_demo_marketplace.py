#!/usr/bin/env python3
"""
Crea o restaura cuentas de prueba para probar el marketplace y el carrito.

Uso (con .venv activado):
    python crear_demo_marketplace.py
"""
from decimal import Decimal

from app.factories.app_factory import create_app
from app.factories.service_factory import get_service_factory


def main():
    app = create_app('development')
    with app.app_context():
        sf = get_service_factory()
        auth = sf.get_auth_service()
        usuarios = sf.get_usuario_repository()
        productos = sf.get_producto_service()
        obras = sf.get_obra_service()

        print('\n=== Usuarios en tu base de datos ===')
        todos = usuarios.get_all(limit=100)
        if not todos:
            print('(No hay usuarios. Ejecuta antes: python init_db.py)')
        for u in todos:
            print(f'  - {u.username:20} | {u.email:30} | rol={u.rol:8} | estado={u.estado}')

        demos = [
            {
                'nombre': 'María González',
                'username': 'maria_artista',
                'email': 'maria.artista@example.com',
                'password': 'artista123',
                'rol': 'artista',
                'biografia': 'Artista de prueba (obras de ejemplo)',
                'estado': 'activo',
            },
            {
                'nombre': 'Cliente Demo',
                'username': 'cliente_demo',
                'email': 'cliente.demo@example.com',
                'password': 'cliente123',
                'rol': 'cliente',
                'biografia': 'Cuenta cliente para probar compras',
                'estado': 'activo',
            },
        ]

        artista = None
        for datos in demos:
            user = usuarios.get_by_email(datos['email'])
            if user:
                user.rol = datos['rol']
                user.estado = 'activo'
                user.password = auth.encriptar_password(datos['password'])
                usuarios.save()
                print(f'\nActualizado: {datos["username"]} (rol={datos["rol"]})')
            else:
                ok, user, errs = auth.registrar_usuario(datos)
                if ok:
                    print(f'\nCreado: {datos["username"]}')
                else:
                    print(f'\nError creando {datos["username"]}: {errs}')
                    continue
            if datos['rol'] == 'artista':
                artista = user

        # Si existe "michael" como cliente, ofrecer convertirlo
        michael = usuarios.get_by_username('michael')
        if not michael:
            for u in todos:
                if u.username and 'michael' in u.username.lower():
                    michael = u
                    break
        if michael:
            if michael.rol != 'artista':
                print(
                    f'\nNota: "{michael.username}" tiene rol "{michael.rol}". '
                    'Por eso no puede subir obras ni productos.'
                )
            else:
                print(
                    f'\nNota: tu usuario "{michael.username}" (email: {michael.email}) '
                    'YA es artista. Inicia sesion con ese email o username "mike", no solo "michael".'
                )

        if not artista:
            artista = usuarios.get_by_email('maria.artista@example.com')
        if not artista:
            print('\nNo se pudo preparar un artista demo.')
            return

        # Producto de prueba para el carrito
        lista = productos.get_by_artista(artista.id_usuario, disponibles_only=False)
        if lista:
            print(f'\nEl artista ya tiene {len(lista)} producto(s).')
            for p in lista:
                print(f'  - {p.nombre} | ${p.precio} | stock={p.stock}')
        else:
            data = {
                'id_artista': artista.id_usuario,
                'nombre': 'Print — Atardecer en el Campo',
                'descripcion': 'Reproducción en alta calidad de la obra exhibida.',
                'precio': float(Decimal('450.00')),
                'stock': 10,
                'imagen': '/static/uploads/obra1.jpg',
            }
            ok, prod = productos.crear_producto(data, artista.id_usuario)
            if ok:
                print('\nProducto demo creado para el marketplace.')
            else:
                print('\nNo se pudo crear el producto demo.')

        print('\n' + '=' * 50)
        print('CUENTAS PARA PROBAR (guárdalas)')
        print('=' * 50)
        print('\nARTISTA (crear obras / productos):')
        print('  Usuario: maria_artista')
        print('  Email:   maria.artista@example.com')
        print('  Clave:   artista123')
        print('\nCLIENTE (carrito y compra):')
        print('  Usuario: cliente_demo')
        print('  Email:   cliente.demo@example.com')
        print('  Clave:   cliente123')
        print('\nO usa tu cuenta Melissa como cliente.')
        print('\nFlujo: login artista -> Productos -> Nuevo producto')
        print('       login cliente -> Marketplace -> Agregar al carrito')
        print('=' * 50 + '\n')


if __name__ == '__main__':
    main()
