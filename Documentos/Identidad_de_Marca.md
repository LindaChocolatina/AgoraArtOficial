# Manual de Identidad de Marca — Ágora Art 🚀🎨

Este documento recopila las directrices visuales, paletas de colores, tipografías y reglas de diseño utilizadas en la interfaz de **Ágora Art**. Su objetivo es servir como guía de referencia rápida para asegurar la consistencia visual en todas las vistas de la plataforma.

---

## 🌌 Concepto de la Marca
Ágora Art se define visualmente bajo el concepto de **"Paleta Espacial Cósmica"** combinada con un diseño limpio, moderno e interactivo inspirado en plataformas de portafolios profesionales (como Behance). Busca transmitir creatividad, profundidad y profesionalismo, haciendo que las obras de arte sean las protagonistas.

---

## 🎨 Paleta de Colores

Nuestra paleta está diseñada para funcionar perfectamente tanto en **Modo Claro (Light Mode)** como en **Modo Oscuro (Dark Mode)** de manera unificada.

### 1. Colores de Identidad (Acentos)
*   **Púrpura Cósmico (Color Principal/Acento)**: `#8B5CF6` (`--cosmic-purple`)
    *   *Uso*: Enlaces, botones principales, estados activos, avatares por defecto y elementos destacados de la marca.
    *   *Variante Hover (Al pasar el mouse)*: `#7C3AED` (`--cosmic-purple-hover`).
*   **Rosa Cósmico (Color de Llamado a la Acción - CTA)**: `#FF2D95` (`--cosmic-pink`)
    *   *Uso*: Reservado **exclusivamente** para botones o llamadas a la acción de máxima prioridad (ej. botón de registro o banner principal en el Hero).
    *   *Variante Hover*: `#e62283` (`--cosmic-pink-hover`).

### 2. Paleta en Modo Oscuro (Cosmic Deep Space)
Para dar esa sensación de "espacio cósmico", utilizamos tonos azul-morados oscuros y profundos en lugar de negros puros:
*   **Fondo Principal (Canvas)**: `#0D0B21` (`--theme-bg`)
*   **Fondo Secundario**: `#12102B` (`--theme-bg-secondary`)
*   **Superficie de Tarjetas/Modales**: `#1A1735` (`--theme-surface`)
*   **Bordes / Divisiones**: `rgba(255, 255, 255, 0.12)` (`--theme-border`)

### 3. Paleta en Modo Claro
Para mantener el minimalismo y la claridad:
*   **Fondo Principal (Canvas)**: `#FFFFFF` (`--theme-bg`)
*   **Fondo Secundario**: `#F8F8F8` (`--theme-bg-secondary`)
*   **Superficie de Tarjetas/Modales**: `#FFFFFF` (`--theme-surface`)
*   **Bordes / Divisiones**: `#ECECEC` (`--theme-border`)

### 4. Escala de Textos (Contraste)
*   **Texto Principal**: `#FFFFFF` (en Modo Oscuro) / `#191919` (en Modo Claro).
*   **Texto Secundario (Muted)**: `rgba(255, 255, 255, 0.72)` (Oscuro) / `#6E6E6E` (Claro).
*   **Texto Sutil (Subtle)**: `rgba(255, 255, 255, 0.52)` (Oscuro) / `#8C8C8C` (Claro).

---

## ✍️ Familia Tipográfica

Utilizamos una jerarquía limpia con dos fuentes principales (cargadas desde Google Fonts):

1.  **Para Títulos y Encabezados (`<h1>` hasta `<h6>`)**:
    *   **Familia**: `'Outfit', sans-serif`
    *   **Peso recomendado**: Negrita / Bold (`700`).
    *   **Altura de línea (Line-height)**: `1.25`
    *   *Por qué la usamos*: Outfit es una tipografía geométrica, moderna y con mucha personalidad, ideal para títulos llamativos y elegantes.

2.  **Para Textos de Cuerpo, Párrafos, Botones e Interfaz (UI)**:
    *   **Familia**: `'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
    *   **Tamaño base**: `14px` (con `line-height: 1.5` o `1.6` para párrafos).
    *   *Por qué la usamos*: Plus Jakarta Sans es extremadamente legible en pantallas de cualquier tamaño y tiene un aspecto muy limpio y profesional.

---

## 📐 Elementos Clave del Diseño Visual

Para que cualquier nueva página que crees se vea "como de Ágora Art", debes seguir estas reglas de estilo:

### 1. Bordes Redondeados (Border Radius)
Evitamos esquinas totalmente cuadradas o afiladas para dar una sensación más amigable y moderna:
*   **Pequeño (`8px`)**: Para campos de entrada (formularios), alertas y pequeños botones.
*   **Mediano (`12px`)**: Para tarjetas de obras de arte, imágenes de perfil y contenedores medianos.
*   **Grande (`16px`)**: Para modales y grandes paneles.
*   **Píldora (`100px`)**: Para botones generales, etiquetas de filtro y barras de búsqueda.

### 2. Sombras (Shadows)
Las sombras dan profundidad a la interfaz:
*   **Sombra Suave**: `0 1px 3px rgba(0,0,0,0.06)` (para tarjetas en estado normal).
*   **Sombra Media**: `0 4px 16px rgba(0,0,0,0.08)` (para tarjetas al pasar el cursor o modales).
*   **Sombra de Hover**: `0 8px 30px rgba(0,0,0,0.12)` (cuando el usuario interactúa).

### 3. Micro-animaciones y Transiciones
Todos los elementos interactivos (botones, enlaces, tarjetas) deben cambiar de estado de forma suave:
*   **Regla general**: `transition: all 0.2s ease;`
*   *Efecto Hover en Tarjetas*: Se elevan ligeramente (`transform: translateY(-4px)`) y aumentan su sombra.

---

## 🛸 Identidad de Elementos Clave (Logo & Hero)

Aquí tienes la descripción detallada y la justificación conceptual de dos de los pilares visuales más importantes de nuestra plataforma:

### 1. El Isotipo / Logo (El Platillo y la "A" Cósmica)
*   **Descripción Visual**: El isotipo consta de un contenedor cuadrado de color **Púrpura Cósmico (`#8B5CF6`)** con bordes suavemente redondeados (`6px`). En su interior, hay un platillo volador blanco minimalista que proyecta un haz de luz cónico hacia abajo, abduciendo una pequeña forma orgánica brillante.
*   **Justificación Conceptual**:
    *   **La "A" oculta (Juego Visual)**: El haz de luz del platillo y el objeto flotante forman de manera muy ingeniosa la letra **"A"** (la inicial de Ágora Art). El contorno del haz simula las patas de la "A", y la figura abducida hace las veces del travesaño medio.
    *   **Abducción Creativa (Captura del Talento)**: El platillo abduciendo un objeto representa la misión de Ágora Art: "raptar" o capturar el talento artístico independiente del mundo ordinario para elevarlo a un plano superior.
    *   **Foco y Luz (El Escenario)**: El haz de luz simboliza el reflector, el foco de atención sobre el artista y su obra, haciendo que sus creaciones brillen y destaquen en la plataforma.

### 2. La Imagen del Hero (`hero_indie.webp`)
*   **Descripción Visual**: Es una ilustración digital de estilo "indie" contemporáneo que muestra un espacio exterior con estrellas y un platillo volador en tonos oscuros y profundos. Está integrada directamente como fondo de la primera sección de la página de inicio.
*   **Justificación Conceptual**:
    *   **Coherencia del Refugio**: Al usar fondos muy oscuros en combinación con el tono `#0D0B21`, se funde invisiblemente con el fondo general del sitio web en modo oscuro, dando una sensación de continuidad espacial y de "inmersión completa".
    *   **Estilo Contemporáneo e Indie**: No es una fotografía aburrida de pinceles o lienzos tradicionales; es una ilustración digital de vanguardia. Esto le dice inmediatamente al usuario que Ágora Art no es una galería tradicional y aburrida, sino un refugio moderno para el arte alternativo, indie y digital.
    *   **El "Impulso Cósmico"**: La presencia del OVNI y las estrellas le da sentido a nuestra frase de bienvenida (*"Donde el Talento Encuentra su Impulso Cósmico"*), transportando al usuario a una experiencia creativa fuera de este mundo.

---

## 📜 Propósito y Misión de Ágora Art
* **Propósito:** Facilitar que artistas independientes expongan, vendan y moneticen sus obras sin barreras de intermediarios.
* **Misión:** Crear una comunidad digital donde el talento artístico sea descubierto, colaborado y premiado, ofreciendo una experiencia premium tanto para creadores como para coleccionistas.

## 🗣️ Tono de Voz y Personalidad
* **Tono:** Cercano, inspirador y apasionado. Hablamos de “tú”, usando un lenguaje sencillo pero profesional.
* **Personalidad:** Creativa, confiable, accesible y un poco juguetona (p.ej., metáforas de espacio y galaxias).

## 📧 Mensajes de Bienvenida y Correos
* Saludo inicial en el sitio: “¡Bienvenido a Ágora Art, tu portal cósmico al arte independiente!”
* Asunto de correo de registro: “Tu cuenta está lista – ¡Despega con Ágora Art!”
* Texto de confirmación: “Gracias por unirte, tu talento está a punto de despegar.”

## 🎨 Uso del Logotipo – Variantes y Prohibiciones
* **Versión completa (icono + texto)** se usa en encabezados y pies de página.
* **Solo isotipo** (el platillo) se usa como favicon y avatar de usuarios sin foto.
* **Versiones de color:**
  - **Oscura:** Logotipo blanco sobre fondo `#0D0B21`.
  - **Clara:** Logotipo morado (`#8B5CF6`) sobre fondo blanco o gris claro.
* **Prohibiciones:**
  - No estirar o deformar el logotipo.
  - No aplicar filtros de color o sombras que alteren su forma.
  - No usar el isotipo morado sobre fondos rosa brillante ni la versión blanca sobre fondos claros.

## 🖼️ Directrices de Imágenes
* **Obras de arte:** Deben ocupar todo el contenedor, usar `object-fit: cover`, preferentemente en formato WebP.
* **Imágenes de portada / hero:** Deben ser ilustraciones de estilo indie, de alta resolución (≥1920 px ancho), con paleta que armonice con la paleta cósmica.
* **Fondo de tarjetas:** Utilizar colores neutros (`var(--gray-100)` o `var(--theme-surface)`) para que la obra destaque.
* **Derechos:** Todas las imágenes deben contar con licencia adecuada (CC‑BY, CC‑0, o derechos del autor).

## 📚 Iconografía
* **Bibliotecas:** FontAwesome (versión 6) y Bootstrap Icons, siempre en estilo “outline” o “thin”.
* **Consistencia:** Mantener un grosor de trazo entre 1 px y 1.5 px. No mezclar íconos gruesos con íconos finos en la misma sección.

## 🔑 Palabras Clave de la Marca
* Innovación, comunidad, descubrimiento, talento, accesibilidad, cosmos, arte independiente.

---

