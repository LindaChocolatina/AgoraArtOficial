# Ágora Art — reglas del proyecto

## Arquitectura

Mantén una separación clara entre la lógica de negocio y la interfaz. Usa componentes modulares y reutilizables.

## Base de datos

**PostgreSQL** es la base de datos de referencia (producción en Coolify vía `DATABASE_URL`). SQLite solo sirve como respaldo local si no hay `DATABASE_URL` configurada (`config.py`).

- Escribe modelos, consultas y migraciones pensando en **PostgreSQL** (tipos, constraints, índices).
- Evita SQL o APIs exclusivas de SQLite (`AUTOINCREMENT` manual, `datetime('now')`, etc.); usa SQLAlchemy portable.
- Los cambios de esquema van con **Flask-Migrate / Alembic** (`migrations/versions/`), no scripts ad hoc que solo funcionen en SQLite.
- En tests se puede usar `sqlite:///:memory:` (`TestingConfig`); no asumas que producción es SQLite.

## Estética UI/UX

El diseño no debe ser frío. La plataforma está inspirada en "arte abducido": prioriza soluciones que permitan una narración inmersiva y detalles que evoquen un espacio para artistas independientes.

## Rendimiento

No añadas librerías de animaciones pesadas. Si se puede hacer con CSS puro o una micro-librería, hazlo así.

---

Fecha de creación: 2026-05-24
