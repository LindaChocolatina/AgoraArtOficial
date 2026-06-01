#!/usr/bin/env python3
"""
Diagnóstico de conexión a Postgres (Coolify / túnel DBeaver).

Uso:
    python scripts/probar_conexion_postgres.py
"""
from pathlib import Path
import os
import sys
import socket

_ROOT = Path(__file__).resolve().parent.parent
os.chdir(_ROOT)
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv

load_dotenv(_ROOT / '.env')

raw = os.environ.get('DATABASE_URL') or os.environ.get('MIGRATE_TARGET_URL')
if not raw:
    print('ERROR: No hay DATABASE_URL ni MIGRATE_TARGET_URL en .env')
    sys.exit(1)

from urllib.parse import urlparse

p = urlparse(
    raw.replace('postgresql+psycopg://', 'postgresql://').replace('postgres://', 'postgresql://')
)
host = p.hostname or '?'
port = p.port or 5432
user = p.username or '?'
db = (p.path or '/').lstrip('/') or '?'

print('--- DATABASE_URL (sin contraseña) ---')
print(f'  usuario: {user}')
print(f'  host:    {host}')
print(f'  puerto:  {port}')
print(f'  base:    {db}')
print()

# ¿Hay algo escuchando en ese host:puerto?
targets = [(host, port)]
if host == '127.0.0.1':
    targets.append(('127.0.0.1', 5441))
    targets.append(('89.117.53.189', 5441))

seen = set()
for h, pt in targets:
    key = (h, pt)
    if key in seen:
        continue
    seen.add(key)
    try:
        s = socket.create_connection((h, pt), timeout=3)
        s.close()
        print(f'  TCP {h}:{pt} -> ABIERTO (algo responde)')
    except OSError as e:
        print(f'  TCP {h}:{pt} -> CERRADO ({e})')

print()
print('--- Prueba PostgreSQL (driver) ---')
url = raw.replace('postgresql+psycopg://', 'postgresql://').replace('postgres://', 'postgresql://')

def _connect():
    try:
        import psycopg
        return psycopg.connect(url, connect_timeout=5)
    except ModuleNotFoundError:
        pass
    try:
        import psycopg2
        return psycopg2.connect(url, connect_timeout=5)
    except ModuleNotFoundError:
        print('  FALLO: instala el driver con:')
        print('     py -m pip install "psycopg[binary]>=3.2.6"')
        print('  (o, si falla: py -m pip install psycopg2-binary)')
        sys.exit(1)

try:
    conn = _connect()
    conn.close()
    print('  OK: conexión PostgreSQL correcta')
except Exception as e:
    print(f'  FALLO: {type(e).__name__}: {e}')
    print()
    print('--- Qué hacer ---')
    if host == '127.0.0.1':
        print('  El puerto 5441 está CERRADO: el túnel SSH no está activo.')
        print('  1. Abre DBeaver → conexión a master_db → clic en Conectar (icono enchufe).')
        print('     Debe quedar conectada (no solo guardada en la lista).')
        print('  2. En la conexión: SSH → "Use SSH Tunnel" activado, puerto local 5441.')
        print('  3. Vuelve a ejecutar: py scripts/probar_conexion_postgres.py')
        print('  4. Alternativa sin DBeaver (deja esta ventana abierta):')
        print('     ssh -i %USERPROFILE%\\.ssh\\id_ed25519 -L 5441:127.0.0.1:5432 root@89.117.53.189 -N')
        print('     (Ajusta 5432 si en Coolify el Postgres interno usa otro puerto.)')
    else:
        print('  Comprueba firewall del VPS y que el puerto esté publicado en Coolify.')
