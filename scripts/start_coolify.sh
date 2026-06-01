#!/bin/sh
set -e
# Migraciones al arrancar (red Coolify), no en el build de la imagen.
flask db upgrade
exec gunicorn --bind "0.0.0.0:${PORT:-5000}" run:app
