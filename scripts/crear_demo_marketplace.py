#!/usr/bin/env python3
"""
Crea o restaura cuentas de prueba para el marketplace y el carrito.

Uso:
    python scripts/crear_demo_marketplace.py
"""
from pathlib import Path
import os
import sys

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

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

        print('\n=== Usuarios en tu base de datos ===')
        todos = usuarios.get_all(limit=100)
        if not todos:
            print('(No hay usuarios. Ejecuta antes: python scripts/init_db.py)')
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

        if not artista:
            artista = usuarios.get_by_email('maria.artista@example.com')
        if not artista:
            print('\nNo se pudo preparar un artista demo.')
            return

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
            ok, _ = productos.crear_producto(data, artista.id_usuario)
            if ok:
                print('\nProducto demo creado para el marketplace.')
            else:
                print('\nNo se pudo crear el producto demo.')

        print('\n' + '=' * 50)
        print('CUENTAS PARA PROBAR')
        print('=' * 50)
        print('\nARTISTA: maria_artista / artista123')
        print('CLIENTE: cliente_demo / cliente123')
        print('=' * 50 + '\n')


if __name__ == '__main__':
    main()
