# Ágora Art — Lista de pendientes

Última actualización: mayo 2026.  
Referencia: `Historias de usuario.pdf` (18 HU, 5 sprints).

**Leyenda:** ✅ hecho · 🟡 a medias · ❌ falta · 🔮 para más adelante (no urgente)

---

## Resumen rápido

| Área | Estado aproximado |
|------|-------------------|
| Historias de usuario (PDF) | ~**80–85 %** (subió tras checkout, direcciones, newsletter, comentarios blog, etc.) |
| Producción (Coolify + Postgres) | ✅ **Web en vivo** |
| “Red social” con varios usuarios | ✅ Datos en BD persisten; ver **volumen de imágenes** abajo |
| Pasarela real (Stripe / Mercado Pago) | 🔮 Extra (la HU 16 pide solo pago simulado) |

---

## Sprint 1 — Entrada

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 1 | Página de inicio | ✅ | Pulir responsive / detalles UI si quieres |
| 2 | Registro | ✅ | 🔮 Verificación de correo real (abajo) |
| 3 | Inicio de sesión | 🟡 | ✅ Recuperar contraseña hecho · ❌ anti fuerza bruta (límite intentos / bloqueo temporal) |

---

## Sprint 2 — Perfiles y admin

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 4 | Perfil artista | ✅ | Ubicación y enlaces en prod (María OK vía SQL); revisar otros artistas si hace falta |
| 5 | Dashboard cliente | 🟡 | ✅ Pestañas estilo Pinterest (favoritos / lienzos / compras) · ❌ **carrito persistente en BD** · ❌ preferencias de categorías · ❌ “actualizaciones” claras de artistas seguidos |
| 6 | Gestión usuarios (admin) | ✅ | — |

---

## Sprint 3 — Obras, categorías, direcciones

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 7 | Publicar obras | ✅ | — |
| 8 | Categorías de obras | 🟡 | ❌ **Varias categorías por obra** (hoy: una sola) |
| 9 | Perfil público artista | ✅ | — |
| 10 | Gestión de direcciones | ✅ | Hecho (crear, editar, eliminar, reglas si usada en compra) |
| 11 | Dirección en la compra | ✅ | Hecho (elegir guardada o nueva en checkout) |

---

## Sprint 4 — Tienda y exploración

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 12 | Crear productos | ✅ | — |
| 13 | Listado de artistas | ✅ | — |
| 14 | Filtrar artistas por categoría | ❌ | Implementar filtro en `/artistas` (hoy solo búsqueda por nombre) |
| 15 | Agregar al carrito | ✅ | ❌ **Favoritos de productos** (si lo quieres como extra; obras favoritas sí hay) |

---

## Sprint 5 — Pago, newsletter, moderación

| # | Historia | Estado | Pendiente |
|---|----------|--------|-----------|
| 16 | Pago simulado | ✅ | La HU pide simulación, no cobro real |
| 17 | Newsletter | ✅ | Botón suscribir/cancelar en perfil artista |
| 18 | Moderación (admin) | 🟡 | ❌ Panel de moderación, reportes, avisos al artista (hoy: visibilidad de obras) |

---

## Extras del proyecto (no están en el PDF pero importan)

| Tema | Estado | Pendiente |
|------|--------|-----------|
| Blog del artista + **comentarios** | ✅ | — |
| Moodboards / lienzos (cliente) | ✅ | Pulir UX si hace falta |
| CMS artista (obras, blog, productos, portafolio) | 🟡 | Pulir flujos, textos “Portafolio”, subida de imágenes |
| CMS cliente (Mi espacio) | 🟡 | Fase Pinterest avanzada; coherencia con HU 5 |
| Tema oscuro / Explorar / Marketplace UI | 🟡 | Detalles visuales que vayan saliendo |
| 2FA | ❌ | Solo mencionado en README; no implementado |
| Pasarela **real** (Stripe en producción) | 🔮 | Claves en Coolify, webhooks, pruebas — después de cerrar HU |

---

## Producción, Coolify e infraestructura

| Tema | Estado | Pendiente |
|------|--------|-----------|
| App Flask en Coolify | ✅ | — |
| Postgres en Coolify (`DATABASE_URL` interno) | ✅ | — |
| Puerto / Gunicorn / variables (`SECRET_KEY`, `FLASK_ENV`) | 🟡 | Revisar que sigan bien tras cada redeploy |
| **Volumen persistente para imágenes** (`static/uploads`) | ❌ | Sin volumen, un **Redeploy** puede borrar fotos subidas (texto en BD queda, rutas rotas). Configurar en Coolify cuando toque (te guiamos paso a paso; no es “chino”, es “carpeta que no se borra”) |
| Dominio propio + HTTPS | 🔮 | Hoy URL `sslip.io` → “No es seguro” en el navegador |
| Backups de Postgres | 🔮 | Activar / revisar en Coolify antes de abrir a mucha gente |
| `Procfile` / `nixpacks.toml` en GitHub | 🟡 | Subir si aún no están en remoto (ayuda a despliegues) |
| `NIXPACKS_NODE_VERSION` en Coolify | 🟡 | Opcional limpiar cuando un redeploy estable no lo necesite |
| README ampliado | 🟡 | Local; commitear solo si tú quieres |

---

## Base de datos y migración

| Tema | Estado | Pendiente |
|------|--------|-----------|
| Postgres producción con datos (artistas, obras, etc.) | ✅ | — |
| Perfiles completos (ubicación, enlaces) | 🟡 | María OK; otros artistas: datos propios o vacíos (cuidado con `UPDATE` sin `WHERE` en DBeaver) |
| Migración completa SQLite → Postgres (`--confirmar`) | 🔮 | Solo si quieres clonar **todo** el `.db` local; borra y reemplaza prod |
| Sincronizar solo perfiles (`--solo-perfiles`) | 🔮 | Script listo; requiere túnel SSH o SQL manual en DBeaver |
| DBeaver | ✅ | Aprendido: **Ctrl+Enter** ejecuta SQL (Enter solo baja línea) |

---

## Correo y cuentas (para más adelante)

| Tema | Cuándo | Notas |
|------|--------|-------|
| Correo “real” al registrarse | 🔮 | Hoy: formato `@` + no duplicado. Lo habitual: cuenta `pendiente` + email con enlace de confirmación (como restablecer contraseña) |
| `email-validator` más estricto | 🔮 | Rechaza formatos raros; **no** prueba que el buzón exista |
| Gmail / `MAIL_*` en Coolify | 🟡 | Restablecer contraseña; revisar en prod que no quede en modo demo |

---

## Orden sugerido (cuando vuelvas a Ágora)

1. **HU 14** — Filtro artistas por categoría (única HU ❌ del PDF).
2. **HU 5** — Carrito persistente en BD (si quieres cumplir la HU al pie de la letra).
3. **HU 8** — Varias categorías por obra.
4. **HU 18** — Moderación admin.
5. **HU 3** — Anti fuerza bruta en login.
6. **Volumen uploads en Coolify** — Antes de que mucha gente suba fotos en prod.
7. Pulir **CMS artista/cliente** y marketplace.
8. 🔮 Verificación email, dominio HTTPS, Stripe real, 2FA, backups.

---

## Hecho recientemente (no repetir)

- Checkout + direcciones (HU 10, 11)
- Comentarios en blog
- Restablecer contraseña + email (demo/prod según config)
- Newsletter en perfil artista (HU 17)
- Seguir artista / favoritos obras (arreglos CSRF y rutas)
- Dashboard cliente con pestañas
- Despliegue Coolify funcionando
- Perfil María: ubicación y enlaces en Postgres (SQL DBeaver)

---

*Para retomar con la IA: “Seguimos Ágora Art; mira `Documentos/PENDIENTES.md`”.*
