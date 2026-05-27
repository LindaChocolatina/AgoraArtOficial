#!/usr/bin/env python
"""
Copia los datos de SQLite local (app/art_platform.db) a PostgreSQL (Coolify).

Uso (desde la raíz del proyecto, túnel SSH abierto):
  1. En .env define DATABASE_URL apuntando al Postgres destino.
  2. Ejecuta:
       python scripts/migrar_sqlite_a_postgres.py --solo-esquema
       python scripts/migrar_sqlite_a_postgres.py --confirmar
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))
load_dotenv(_ROOT / '.env')

SOURCE_SQLITE = _ROOT / 'app' / 'art_platform.db'

TABLES_ORDER = [
    'categorias',
    'usuarios',
    'obras',
    'obra_imagenes',
    'productos',
    'producto_imagenes',
    'historial_stock',
    'entradas_blog',
    'comentarios_blog',
    'direcciones',
    'ordenes',
    'orden_items',
    'pagos',
    'lienzos',
    'lienzo_items',
    'newsletters',
    'suscripciones',
    'favoritos_obras',
    'favoritos_artistas',
    'bandeja_newsletter',
    'auditoria',
]

SEQUENCE_COLUMNS = {
    'usuarios': 'id_usuario',
    'categorias': 'id_categoria',
    'obras': 'id_obra',
    'obra_imagenes': 'id_imagen',
    'productos': 'id_producto',
    'producto_imagenes': 'id_imagen',
    'historial_stock': 'id_historial',
    'entradas_blog': 'id_entrada',
    'comentarios_blog': 'id_comentario',
    'direcciones': 'id_direccion',
    'ordenes': 'id_orden',
    'orden_items': 'id_item',
    'pagos': 'id_pago',
    'lienzos': 'id_lienzo',
    'lienzo_items': 'id_item',
    'newsletters': 'id_newsletter',
    'suscripciones': 'id_suscripcion',
    'auditoria': 'id_auditoria',
}


def _normalize_url(url: str) -> str:
    if url.startswith('postgres://'):
        url = 'postgresql://' + url[len('postgres://'):]
    if url.startswith('postgresql://') and not url.startswith('postgresql+'):
        url = 'postgresql+psycopg://' + url[len('postgresql://'):]
    return url


def _ensure_schema(target_url: str):
    from flask_migrate import upgrade
    from app.factories.app_factory import create_app, _ensure_dev_schema_patches

    env_url = target_url.replace('postgresql+psycopg://', 'postgresql://')
    os.environ['DATABASE_URL'] = env_url

    app = create_app('production')
    with app.app_context():
        print('Aplicando migraciones Alembic en Postgres...')
        upgrade()
        print('Aplicando parches de columnas nuevas...')
        _ensure_dev_schema_patches()
        print('Esquema listo.')


def _copy_data(source_url: str, target_url: str):
    from sqlalchemy import create_engine, inspect, text

    src = create_engine(source_url)
    dst = create_engine(target_url)

    src_insp = inspect(src)
    dst_insp = inspect(dst)
    src_tables = set(src_insp.get_table_names())
    dst_tables = set(dst_insp.get_table_names())

    with dst.connect() as conn:
        conn.execute(text('SET session_replication_role = replica'))
        for table in reversed(TABLES_ORDER):
            if table in dst_tables:
                conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
        conn.commit()

    total_rows = 0
    with src.connect() as sconn, dst.connect() as dconn:
        for table in TABLES_ORDER:
            if table not in src_tables:
                print(f'  omitida (no en SQLite): {table}')
                continue
            if table not in dst_tables:
                print(f'  omitida (no en Postgres): {table}')
                continue

            rows = sconn.execute(text(f'SELECT * FROM "{table}"')).mappings().all()
            if not rows:
                print(f'  {table}: 0 filas')
                continue

            cols = list(rows[0].keys())
            col_list = ', '.join(f'"{c}"' for c in cols)
            placeholders = ', '.join(f':{c}' for c in cols)
            insert_sql = text(f'INSERT INTO "{table}" ({col_list}) VALUES ({placeholders})')

            for row in rows:
                dconn.execute(insert_sql, dict(row))
            dconn.commit()
            total_rows += len(rows)
            print(f'  {table}: {len(rows)} filas')

        for table, pk_col in SEQUENCE_COLUMNS.items():
            if table not in dst_tables:
                continue
            dconn.execute(text(
                f"SELECT setval(pg_get_serial_sequence('{table}', '{pk_col}'), "
                f"COALESCE((SELECT MAX(\"{pk_col}\") FROM \"{table}\"), 1), true)"
            ))
        dconn.commit()

        dconn.execute(text('SET session_replication_role = origin'))
        dconn.commit()

    print(f'\nMigración completada: {total_rows} filas copiadas.')


def main():
    parser = argparse.ArgumentParser(description='Migrar SQLite local → PostgreSQL Coolify')
    parser.add_argument('--confirmar', action='store_true', help='Ejecutar copia de datos (borra Postgres destino)')
    parser.add_argument('--solo-esquema', action='store_true', help='Solo migraciones y parches de esquema')
    args = parser.parse_args()

    if not SOURCE_SQLITE.is_file():
        print(f'No se encontró {SOURCE_SQLITE}', file=sys.stderr)
        sys.exit(1)

    target = os.environ.get('DATABASE_URL') or os.environ.get('MIGRATE_TARGET_URL')
    if not target:
        print(
            'Falta DATABASE_URL en .env (URL de Postgres en Coolify o túnel local).\n'
            'Coolify → Environment Variables → copia DATABASE_URL → pégala en .env',
            file=sys.stderr,
        )
        sys.exit(1)

    target = _normalize_url(target)
    source = f'sqlite:///{SOURCE_SQLITE.as_posix()}'

    print(f'Origen:  {SOURCE_SQLITE}')
    print(f'Destino: {target.split("@")[-1] if "@" in target else target}')

    _ensure_schema(target)

    if args.solo_esquema:
        print('Solo esquema (--solo-esquema). Datos no modificados.')
        return

    if not args.confirmar:
        print('\nPara copiar datos (REEMPLAZA todo en Postgres), ejecuta:')
        print('  python scripts/migrar_sqlite_a_postgres.py --confirmar')
        sys.exit(0)

    print('\nCopiando datos (esto borra y reemplaza tablas en Postgres)...')
    _copy_data(source, target)
    print('\nListo. Haz Redeploy en Coolify si la app ya estaba corriendo.')


if __name__ == '__main__':
    main()
