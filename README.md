# Ágora Art 🎨
**Un refugio digital para el arte independiente, libre de algoritmos.**

Ágora Art es una plataforma integral diseñada para conectar a creadores y coleccionistas en un entorno minimalista, profesional y estéticamente cuidado. Inspirada en la limpieza visual de Behance y enfocada en la autonomía del artista, permite la gestión de portafolios, blogs y transacciones comerciales sin intermediarios algorítmicos.

## 🎯 Objetivo del Proyecto
Proporcionar un espacio donde la obra de arte sea la protagonista, eliminando el ruido de las redes sociales convencionales y permitiendo que la comunicación entre artista y coleccionista sea directa y genuina.

---

## 🛠️ Stack Tecnológico
El proyecto está construido bajo estándares modernos de desarrollo web con Python:

*   **Backend:** [Flask](https://flask.palletsprojects.com/) (Microframework de Python)
*   **Base de Datos:** [SQLAlchemy](https://www.sqlalchemy.org/) (ORM) con SQLite para persistencia.
*   **Autenticación:** Flask-Login y Flask-Bcrypt para el hashing de contraseñas.
*   **Frontend:** HTML5, Jinja2, y Vanilla CSS para un control total del diseño (Behance-Style).
*   **Gestión de Formularios:** Flask-WTF con protección CSRF.
*   **Migraciones:** Flask-Migrate.

---

## 🏗️ Estructura del Proyecto (Architecture)
Hemos implementado el **Pattern Factory** para garantizar que la aplicación sea escalable y fácil de testear. La estructura sigue una separación clara de responsabilidades:

```text
Proyecto plataforma/
│
├── app/
│   ├── factories/          # Lógica de creación (App Factory, DB Factory)
│   ├── controllers/        # Blueprints y manejo de rutas (MVC - Controllers)
│   ├── models/             # Definición de tablas y lógica de datos
│   ├── services/           # Lógica de negocio (Capa intermedia)
│   ├── static/             # Archivos CSS, JS e Imágenes
│   └── templates/          # Vistas (HTML con Jinja2)
│
├── instance/               # Archivos de base de datos y configuración local
├── migrations/             # Historial de cambios en la base de datos
├── run.py                  # Punto de entrada de la aplicación
└── README.md               # Documentación general
```

---

## ✨ Características Principales
*   **Multiperfil:** Espacios dedicados para Artistas (gestión de obras) y Clientes (coleccionismo).
*   **Diseño Behance-Style:** Interfaz de alta fidelidad con sistema de descubrimiento, carruseles de categorías y grids de proyectos limpios.
*   **Seguridad:** Implementación de cifrado para credenciales y protección contra ataques comunes (CSRF, Inyecciones).
*   **Arquitectura Modular:** Uso de *Blueprints* para separar la administración, la autenticación y la parte pública.

---

## 🚀 Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/frankalexander-GM/pagina-wed.git
   ```

2. **Configurar el entorno virtual:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación:**
   ```bash
   python run.py
   ```

---

**Desarrollado con ❤️ por el equipo de Ágora Art.**