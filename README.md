# 🛸 Ágora Art: Plataforma de Exhibición Artística
**Un refugio digital para el arte independiente, libre de algoritmos.**

Ágora Art es una plataforma web diseñada para conectar artistas independientes con coleccionistas, bajo una estética surrealista y minimalista. Este proyecto nació de la necesidad de crear un espacio donde el arte no solo se vea, sino que se experimente.

---

## 🧠 Arquitectura y Liderazgo Técnico
Como **Lead Developer**, diseñé y ejecuté la arquitectura modular del sistema, asegurando una base sólida y escalable:

*   **Patrón Application Factory:** Implementación de una estructura limpia para gestionar múltiples entornos (Desarrollo, Producción).
*   **Blueprints:** Organización modular de controladores (Auth, Artista, Cliente, Admin) para garantizar un código limpio y mantenible.
*   **Seguridad y Autenticación:** Integración de sistemas de seguridad robustos, incluyendo **Autenticación de Dos Pasos (2FA)** y validaciones de alta complejidad.
*   **Infraestructura Pro:** Configuración de despliegue automatizado en **Coolify** con base de datos **PostgreSQL** para entornos de producción.

---

## 🎨 Identidad de Marca y Dirección Creativa
Propuse y desarrollé la narrativa visual de **"Arte Abducido"**, definiendo:

*   **Paleta de Colores Cósmica:** Un esquema de colores profundos y vibrantes que evoca el espacio exterior y la introspección.
*   **Estética Minimalista:** Un diseño de alta fidelidad (estilo Behance) que prioriza la obra de arte, eliminando las distracciones visuales comunes en las redes sociales convencionales.
*   **UX Centrada en el Artista:** Herramientas personalizadas para la gestión de portafolios, blogs y banners dinámicos.

---

## 🏗️ Estructura del Proyecto (Sitemap Técnico)
Se ha implementado una arquitectura multicapa (MVC) para la separación de responsabilidades:

```text
Proyecto plataforma/
│
├── app/
│   ├── factories/          # Lógica de creación (App Factory, DB Factory)
│   ├── controllers/        # Blueprints y manejo de rutas
│   ├── models/             # Definición de esquemas de datos (SQLAlchemy)
│   ├── repositories/       # Abstracción de acceso a datos
│   ├── services/           # Capa de lógica de negocio
│   ├── static/             # Assets: CSS cósmico y recursos multimedia
│   └── templates/          # Vistas dinámicas con Jinja2
│
├── instance/               # Configuración local (Privada - No subida a GitHub)
├── migrations/             # Historial de versiones de la Base de Datos
├── .env                    # Secretos y variables de entorno
├── run.py                  # Punto de entrada de la aplicación
└── README.md               # Documentación oficial
```

> **Nota sobre seguridad:** La carpeta `instance/` y el archivo `.env` contienen credenciales sensibles. Siguiendo las mejores prácticas de la industria, estos recursos están protegidos y excluidos del repositorio público.

---

## 🚀 Instalación y Desarrollo Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/LindaChocolatina/AgoraArtOficial.git
   ```

2. **Entorno Virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Instalar Dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

---

**Desarrollado con visión y código por [Linda Chocolatina](https://github.com/LindaChocolatina).** 🛸✨