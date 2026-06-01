# Detrás del Refugio: El Proceso Creativo y Técnico de Ágora Art

Bienvenido al espacio donde el arte hackea al algoritmo. **Ágora Art** no nació solo como un proyecto de desarrollo de software; nació como una respuesta a una necesidad real de la comunidad creativa independiente. Este documento describe el viaje completo: desde la detección del problema hasta el despliegue del ecosistema en producción.

*Proyecto académico — ADSO (Análisis y Desarrollo de Software).*

---

## 1. La chispa: el problema en el mundo real

Las redes sociales tradicionales solían ser un escaparate para el talento, pero hoy están rotas para muchos creadores. Los artistas independientes se enfrentan a tres barreras críticas:

- **La tiranía del algoritmo:** las plataformas actuales premian la hiperproducción de contenido rápido en lugar de la calidad técnica o conceptual de la obra.
- **La dispersión de herramientas:** para gestionar su carrera, un artista debe fragmentarse: un espacio para el portafolio, otro para la comunidad, una plataforma externa para *newsletters* y un e-commerce ajeno para vender.
- **Métricas de vanidad frente a conexión real:** el éxito se mide en interacciones efímeras que no siempre se traducen en mecenazgo, coleccionismo ni estabilidad económica.

**La propuesta:** crear un **refugio creativo** — un ecosistema digital que fusiona la curaduría visual de un portafolio profesional (estilo Behance) con la infraestructura de un marketplace (estilo Etsy), reduciendo el ruido y la dependencia del algoritmo.

---

## 2. Dirección de arte: «Arte abducido» y paleta cósmica

Para alejarnos de interfaces corporativas genéricas o de formatos de inventario fríos, la plataforma tiene una identidad visual definida centrada en la obra.

- **Concepto visual:** «Arte abducido» — narrativa cósmica y minimalista donde la obra es la protagonista y la interfaz no compite con ella.
- **Tema claro / oscuro:** sistema unificado con variables CSS semánticas (`--theme-surface`, `--theme-bg`, etc.) en `theme.css`.
- **Paleta:** modo oscuro sobre **violeta cósmico profundo** (`#0D0B21`); acentos **púrpura** (`#8B5CF6`) y **rosa** (`#FF2D95`) para CTAs y puntos de luz.
- **Isotipo:** platillo volador cuyo haz dibuja la letra **«A»** — la «abducción» del talento hacia un espacio de visibilidad digna.
- **Tipografía y UI:** `Outfit` en títulos, `Plus Jakarta Sans` en cuerpo; **Bootstrap 5** como grid responsive y hojas propias (`agora_art.css`).

---

## 3. Lógica del sistema y arquitectura de software

Ágora Art es una aplicación full-stack con **MVC ampliado** y separación explícita de capas:

| Capa | Rol |
|------|-----|
| **Controllers** (blueprints) | Rutas HTTP, permisos, formularios |
| **Services** | Reglas de negocio (carrito, órdenes, pagos, favoritos, newsletters) |
| **Repositories** | Acceso a datos (SQLAlchemy) |
| **Models** | Esquema relacional |
| **Templates + static** | Vista (Jinja2, CSS, JS ligero) |

- **Application Factory (`create_app`):** arranque por entorno (desarrollo, testing, producción).
- **Blueprints modulares:** Público, Auth, Artista, Cliente, Admin, API.
- **Patrón Repository:** consultas desacopladas de los controladores.
- **Capa Service:** orquesta procesos como carrito persistente, órdenes, moodboards y pagos.

### Ecosistema de roles

- **Administrador:** salud del sistema, usuarios, visibilidad de obras, categorías y auditoría.
- **Artista:** portafolio por categorías, blog con comentarios, tienda con stock, newsletters a suscriptores (bandeja interna).
- **Cliente / coleccionista:** seguir artistas, favoritos, compras, direcciones, newsletters recibidos y lienzos (moodboards).

---

## 4. Stack técnico e infraestructura

- **Backend:** Python 3.14, Flask 2.3, Jinja2 (SSR).
- **Datos:** PostgreSQL en producción, SQLite en local; SQLAlchemy + Flask-Migrate / Alembic.
- **Seguridad:** Flask-Login, bcrypt, CSRF (Flask-WTF), validación de email, bloqueo temporal tras intentos fallidos de login.
- **Medios y correo:** Pillow (imágenes); Flask-Mail (SMTP) para recuperar contraseña.
- **Pagos:** integración Stripe (Checkout + webhooks); **modo demo** para la entrega académica (HU de pago simulado).
- **DevOps:** Git/GitHub; despliegue en **Coolify** (Nixpacks) sobre **VPS Contabo**; **Gunicorn**; migraciones al arrancar (`start_coolify.sh`).

---

## 5. Proceso de desarrollo y alcance

El trabajo se organizó en **18 historias de usuario** (5 sprints): autenticación, perfiles, obras, marketplace, checkout, newsletters y moderación básica. El flujo fue investigación → diseño de marca → modelado de datos → desarrollo iterativo en local → despliegue en Coolify con PostgreSQL.

**Alcance alcanzado (MVP):** plataforma en vivo, roles completos, carrito en BD, tema claro/oscuro, panel admin con centro de control.

**Roadmap (post-entrega):** moderación con reportes, verificación de email al registrarse, 2FA, Stripe en producción con claves reales, volumen persistente para `uploads`, dominio propio con HTTPS.

---

## Cierre

**Ágora Art** demuestra que el desarrollo de software y el arte comparten el mismo núcleo: crear algo significativo a partir de un lienzo en blanco — ya sea un canvas o una base de código.
