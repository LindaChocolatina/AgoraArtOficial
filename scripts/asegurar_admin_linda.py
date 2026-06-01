#!/usr/bin/env python3
"""
Crea o actualiza la cuenta admin de Linda.

Uso (contraseña por variable de entorno, no la pegues en Git):
    set ADMIN_PASSWORD=tu_contraseña
    .venv\\Scripts\\python.exe scripts/asegurar_admin_linda.py
    .venv\\Scripts\\python.exe scripts/asegurar_admin_linda.py --production
"""
from pathlib import Path
import argparse
import os
import sys

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / '.env')
# Evita sembrar categorías al arrancar (solo necesitamos usuarios)
os.environ.setdefault('MIGRATE_SCHEMA_ONLY', '1')

EMAIL = 'lindasioc@gmail.com'
NOMBRE = 'Linda'
USERNAME = 'linda_admin'


def main():
    password = os.environ.get('ADMIN_PASSWORD', '').strip()
    if not password:
        print('Define ADMIN_PASSWORD en el entorno antes de ejecutar.')
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--production',
        action='store_true',
        help='Usar config production (DATABASE_URL en .env)',
    )
    args = parser.parse_args()
    config = 'production' if args.production else 'development'

    from app.factories.app_factory import create_app
    from app.factories.service_factory import get_service_factory
    from app.services.auth_service import AuthService

    app = create_app(config)

    with app.app_context():
        sf = get_service_factory()
        repo = sf.get_usuario_repository()
        auth = AuthService(repo)
        pwd_hash = auth.encriptar_password(password)

        u = repo.get_by_email(EMAIL)
        if u:
            repo.update(
                u.id_usuario,
                {
                    'rol': 'admin',
                    'estado': 'activo',
                    'password': pwd_hash,
                    'nombre': u.nombre or NOMBRE,
                },
            )
            repo.save()
            u = repo.get_by_id(u.id_usuario)
            print('ACTUALIZADO')
        else:
            username = USERNAME
            if repo.username_exists(username):
                username = 'linda_admin2'
            u = repo.create(
                {
                    'nombre': NOMBRE,
                    'username': username,
                    'email': EMAIL.lower(),
                    'password': pwd_hash,
                    'rol': 'admin',
                    'biografia': 'Administradora de Ágora Art',
                    'estado': 'activo',
                },
                registrar_auditoria=False,
            )
            repo.save()
            print('CREADO')

        print(f'id: {u.id_usuario}')
        print(f'nombre: {u.nombre}')
        print(f'username: {u.username}')
        print(f'email: {u.email}')
        print(f'rol: {u.rol}')
        print(f'estado: {u.estado}')


if __name__ == '__main__':
    main()
