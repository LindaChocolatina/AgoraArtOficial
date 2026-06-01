#!/usr/bin/env python3
"""
Aplica migraciones Alembic pendientes (carrito_items, login_bloqueos, etc.).

Uso:
    python scripts/aplicar_migraciones.py

Requiere DATABASE_URL en .env (o la URL interna de Coolify).
"""
from pathlib import Path
import os
import sys

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / '.env')

if not os.environ.get('DATABASE_URL'):
    print('ERROR: Define DATABASE_URL en .env')
    sys.exit(1)

os.environ.setdefault('FLASK_APP', 'run:app')

from run import app
from flask_migrate import current, upgrade


def main():
    with app.app_context():
        before = current()
        print(f'Revisión actual: {before or "(ninguna)"}')
        print('Aplicando migraciones pendientes...')
        upgrade()
        after = current()
        print(f'Revisión final:   {after}')
        if after == before:
            print('No había migraciones pendientes.')
        else:
            print('Listo. Comprueba en DBeaver las tablas carrito_items y login_bloqueos.')


if __name__ == '__main__':
    main()
