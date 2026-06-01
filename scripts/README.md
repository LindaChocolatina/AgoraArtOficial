# Scripts de desarrollo

Utilidades que **no** forman parte del servidor en producción. Ejecutar desde la **raíz** del proyecto:

```powershell
.\.venv\Scripts\activate
python scripts/init_db.py
python scripts/crear_demo_marketplace.py
python scripts/migrar_sqlite_a_postgres.py --solo-esquema
python scripts/migrar_sqlite_a_postgres.py --confirmar
```

| Script | Uso |
|--------|-----|
| `init_db.py` | Crea tablas SQLite locales y datos de ejemplo |
| `crear_demo_marketplace.py` | Cuentas demo artista/cliente + producto de prueba |
| `migrar_sqlite_a_postgres.py` | Esquema y datos: SQLite local → Postgres (Coolify). Requiere túnel SSH y `DATABASE_URL` en `.env` |
| `probar_conexion_postgres.py` | Comprueba host/puerto y si el túnel responde antes de migrar |
| `start_coolify.sh` | Arranque en producción: migraciones + Gunicorn (Start Command en Coolify) |
