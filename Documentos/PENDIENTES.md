# Ágora Art — Lista de pendientes

Última actualización: **junio 2026** (post-presentación).  
Referencia: `Historias de usuario.pdf` (18 HU, 5 sprints).

**Leyenda:** ✅ hecho · 🟡 a medias · ❌ falta · 🔮 para más adelante (no urgente)

---

## Resumen rápido

| Área | Estado aproximado |
|------|-------------------|
| Historias de usuario (PDF) | ~**88–92 %** |
| Producción (Coolify + Postgres) | ✅ **Web en vivo** |
| Cuenta admin Linda (`lindasioc@gmail.com`) | ✅ En Postgres (Coolify) |
| Panel admin — dashboard (Resumen) | ✅ Visibilidad claro/oscuro + guía de pestañas |
| Pasarela real (Stripe) | 🔮 Código listo; falta config + pruebas en Coolify |
| Login “correo real” + 2FA | 🔮 Ver abajo |

---

## Panel de administrador (Centro de Control)

| Tema | Estado | Pendiente |
|------|--------|-----------|
| Acceso admin en producción | ✅ | Login `lindasioc@gmail.com` · rol `admin` (SQL DBeaver o script) |
| **Dashboard / Resumen** | ✅ | Tarjetas legibles en modo claro y oscuro; desglose artistas + clientes + **admins**; texto guía de pestañas |
| Pestaña **Comunidad** (`/admin/usuarios`) | 🟡 | Listar, buscar, activar/bloquear — pulir mismo estilo tema claro/oscuro |
| Pestaña **Galería** (`/admin/obras`) | 🟡 | Ocultar/mostrar obras — pulir UI y contraste |
| Pestaña **Taxonomía** (`/admin/categorias`) | 🟡 | CRUD categorías — pulir UI |
| Pestaña **Seguridad** (`/admin/auditoria`) | 🟡 | Registros de auditoría — pulir UI |
| **Estadísticas** (`/admin/estadisticas`) | 🟡 | Existe; `nuevas_mes` en dashboard sigue en 0 (TODO en código) |
| Moderación completa (HU 18) | ❌ | Reportes de usuarios, cola de revisión, avisos al artista (hoy solo visibilidad de obras) |
| Entender rol admin (documentación) | 🟡 | Guía breve ya en dashboard; opcional: página “Ayuda admin” o tooltip |
| Página **Detrás del proyecto** (proceso creativo/técnico) | ✅ | `/detras-del-proyecto` + `Documentos/DETRAS_DEL_REFUGIO.md` + footer (`/acerca-de` redirige) |

**Qué hace el admin hoy (resumen):** moderar la plataforma — usuarios (Comunidad), obras (Galería), categorías (Taxonomía), trazas del sistema (Seguridad). No es el CMS del artista.

---

## Sprint 1 — Entrada

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 1 | Página de inicio | ✅ | Pulir responsive / detalles UI si quieres |
| 2 | Registro | ✅ | 🔮 Verificación de correo al registrarse (abajo) |
| 3 | Inicio de sesión | ✅ | ✅ Recuperar contraseña · ✅ anti fuerza bruta (`login_bloqueos`) |

---

## Sprint 2 — Perfiles y admin

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 4 | Perfil artista | ✅ | Otros artistas: ubicación/enlaces si hace falta |
| 5 | Dashboard cliente | 🟡 | ✅ Pestañas (favoritos / lienzos / compras / siguiendo) · ✅ **carrito en BD** · ❌ preferencias de categorías · ❌ feed de novedades de artistas seguidos |
| 6 | Gestión usuarios (admin) | ✅ | Pulir vistas admin (ver sección Panel admin) |

---

## Sprint 3 — Obras, categorías, direcciones

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 7 | Publicar obras | ✅ | — |
| 8 | Categorías de obras | 🟡 | ❌ **Varias categorías por obra** (hoy: una sola `id_categoria`) |
| 9 | Perfil público artista | ✅ | — |
| 10 | Gestión de direcciones | ✅ | — |
| 11 | Dirección en la compra | ✅ | — |

---

## Sprint 4 — Tienda y exploración

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 12 | Crear productos | ✅ | — |
| 13 | Listado de artistas | ✅ | — |
| 14 | Filtrar artistas por categoría | ✅ | Implementado en `/artistas` |
| 15 | Agregar al carrito | ✅ | ❌ **Favoritos de productos** (extra; obras favoritas sí) |

---

## Sprint 5 — Pago, newsletter, moderación

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 16 | Pago simulado | ✅ | Cumple el PDF (modo demo / simulación) |
| 17 | Newsletter | ✅ | Bandeja interna; suscribir/cancelar en perfil artista |
| 18 | Moderación (admin) | 🟡 | Visibilidad de obras sí · ❌ panel de reportes / avisos (ver Panel admin) |

---

## Extras del proyecto (fuera del PDF o ampliados)

| Tema | Estado | Pendiente |
|------|--------|-----------|
| Blog + comentarios | ✅ | — |
| Moodboards / lienzos | ✅ | Pulir UX si hace falta |
| CMS artista | 🟡 | Portafolio, galerías, textos |
| CMS cliente (Mi espacio) | 🟡 | Coherencia con HU 5 |
| Tema oscuro / Explorar / Marketplace | 🟡 | Detalles visuales |
| **2FA** | ❌ | No implementado |
| **Stripe real** | 🟡 | `PaymentService` + webhook; poner `STRIPE_*` en Coolify y probar |
| Tests automatizados (`pytest`) | ❌ | Dependencias en `requirements.txt`; sin suite en repo |
| Scripts ops | ✅ | `asegurar_admin_linda.py`, `crear_admin_coolify.ps1`, `POSTGRES_*` en `.env` |

---

## Producción, Coolify e infraestructura

| Tema | Estado | Pendiente |
|------|--------|-----------|
| App Flask en Coolify | ✅ | — |
| Postgres en Coolify | ✅ | — |
| Migraciones al arrancar (`start_coolify.sh`) | ✅ | No usar `flask db upgrade` en build (rompe `postgres-db`) |
| Variables (`SECRET_KEY`, `FLASK_ENV`, `DATABASE_URL`) | 🟡 | Revisar tras cada redeploy |
| **Volumen persistente** `static/uploads` | ❌ | Redeploy puede borrar imágenes subidas |
| Dominio propio + HTTPS | 🔮 | Hoy `sslip.io` → aviso “No es seguro” |
| Backups Postgres | 🔮 | Activar en Coolify antes de mucho tráfico |
| `Procfile` / `nixpacks` en remoto | 🟡 | Confirmar que `second-branch` tenga el fix sin `release: flask db upgrade` |
| README ampliado | 🟡 | Commitear si quieres |

---

## Base de datos y cuentas

| Tema | Estado | Pendiente |
|------|--------|-----------|
| Datos en Postgres (artistas, obras, etc.) | ✅ | — |
| Admin Linda en producción | ✅ | `lindasioc@gmail.com` · rol `admin` |
| Admin por defecto (`admin@artplatform.com`) | 🔮 | Solo local / demo; no usar en prod |
| `.env` local: `POSTGRES_*` para túnel DBeaver | ✅ | Contraseña en `.env` (no subir a Git) |
| Perfiles artistas completos | 🟡 | María OK; otros según necesidad |
| Migración SQLite → Postgres completa | 🔮 | Solo si quieres clonar todo el `.db` local |

---

## Correo y autenticación avanzada

| Tema | Estado | Notas |
|------|--------|-------|
| Restablecer contraseña | ✅ | `Flask-Mail` + plantillas; `MAIL_*` en `.env` |
| Gmail en Coolify | 🟡 | Comprobar que en prod no quede modo demo |
| **Verificación email al registrarse** | ❌ | Hoy: formato + no duplicado; falta enlace de confirmación |
| **2FA** | ❌ | No implementado |
| Login con email + contraseña | ✅ | — |

---

## Orden sugerido (próximos pasos)

1. **Pulir admin** — Comunidad, Galería, Taxonomía, Seguridad (mismo estilo que Resumen).
2. **HU 18** — Reportes / moderación real (si el curso o producto lo exigen).
3. **HU 5** — Preferencias de categorías + feed de artistas seguidos.
4. **HU 8** — Varias categorías por obra.
5. **Volumen uploads** en Coolify (antes de muchas subidas en prod).
6. 🔮 Stripe en prod, verificación email, dominio HTTPS, 2FA, backups.
7. Favoritos de productos, tests, pulido CMS/marketplace.

---

## Hecho recientemente (junio 2026 — no repetir)

- Presentación: plataforma en vivo en Coolify
- Cuenta admin Linda en Postgres (DBeaver / contraseña actualizada)
- **Panel admin — dashboard:** visibilidad modo claro/oscuro, chips de métricas, conteo admins, guía de pestañas
- Config `.env`: `POSTGRES_*` para túnel; scripts `asegurar_admin_linda.py`, `crear_admin_coolify.ps1`
- Fix `create_app`: relee URI tras `load_dotenv`
- (Ya estaba en código, doc desactualizada corregida): anti fuerza bruta, carrito BD, filtro artistas por categoría, Stripe en código

---

## Hecho antes (referencia)

- Checkout + direcciones (HU 10, 11)
- Comentarios en blog
- Newsletter en perfil artista (HU 17)
- Seguir artista / favoritos obras
- Dashboard cliente con pestañas
- Despliegue Coolify + migraciones al arrancar
- Perfil María: ubicación y enlaces (SQL)

---

*Para retomar con la IA: “Seguimos Ágora Art; mira `Documentos/PENDIENTES.md`”.*
