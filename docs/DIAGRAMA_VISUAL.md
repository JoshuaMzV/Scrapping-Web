# 📐 Diagrama Visual de Estructura

## Flujo de Datos en la Aplicación

```
┌─────────────────────────────────────────────────────────────────┐
│                      USUARIO EN NAVEGADOR                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  HTML: templates/index.html                          │       │
│  │  CSS:  static/css/style.css                          │       │
│  │  JS:   static/js/script.js                           │       │
│  └──────────────────────────────────────────────────────┘       │
│                          ↓                                       │
└─────────────────────────────────────────────────────────────────┘
                           ↓ HTTP
                    POST /scrape
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND FLASK (app.py)                        │
│                                                                   │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ 1. Recibe marca y links                              │        │
│  │ 2. Importa scraper según marca                      │        │
│  │    from src.config import MARCAS_SOPORTADAS         │        │
│  └─────────────────────────────────────────────────────┘        │
│                       ↓                                          │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ 3. Para cada URL:                                    │        │
│  │    - Detecta sitio (Nike.com, Amazon, eBay)         │        │
│  │    - Llama scraper correspondiente                  │        │
│  │                                                      │        │
│  │    from scrapers.nike import scrape_nike            │        │
│  └─────────────────────────────────────────────────────┘        │
│                       ↓                                          │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ 4. Scraper extrae datos usando Selenium:            │        │
│  │    • Nombre del producto                            │        │
│  │    • Precio (procesa con limpiar_precio)            │        │
│  │    • Imagen                                         │        │
│  │    • Tallas                                         │        │
│  │    • Sitio detectado                                │        │
│  └─────────────────────────────────────────────────────┘        │
│                       ↓                                          │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ 5. Procesa datos:                                    │        │
│  │    - Limpia precios con helpers.py                  │        │
│  │    - Detecta si necesita tallas (es_producto_...)   │        │
│  │    - Calcula precios finales                        │        │
│  └─────────────────────────────────────────────────────┘        │
│                       ↓                                          │
│  ┌─────────────────────────────────────────────────────┐        │
│  │ 6. Genera Excel en memoria (sin guardar en disco)    │        │
│  │    - Crea DataFrame con pandas                      │        │
│  │    - Codifica en base64                             │        │
│  └─────────────────────────────────────────────────────┘        │
│                       ↓                                          │
└─────────────────────────────────────────────────────────────────┘
                      ↓ JSON
            {filename, excel_data, success}
                      ↓
┌─────────────────────────────────────────────────────────────────┐
│                      NAVEGADOR (JS)                              │
│                                                                   │
│  Pregunta: ¿Descargar archivo?                                   │
│                                                                   │
│  SI ↓                                    NO ↓                    │
│  ┌──────────────┐                   ┌──────────────┐             │
│  │Decodifica    │                   │Solo muestra  │             │
│  │base64       │                   │mensaje éxito │             │
│  │en BLOB      │                   └──────────────┘             │
│  └──────────────┘                                                │
│       ↓                                                           │
│  ┌──────────────────────────────────┐                            │
│  │Abre diálogo "Guardar Como..."    │                            │
│  │Usuario elige dónde guardar:      │                            │
│  │  - Downloads                     │                            │
│  │  - USB                           │                            │
│  │  - Desktop                       │                            │
│  │  - Otro lugar                    │                            │
│  └──────────────────────────────────┘                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Estructura de Carpetas

```
scraping_project/
│
├── 📁 src/                        ← CÓDIGO NUEVO Y ORGANIZADO
│   ├── 📁 config/
│   │   ├── __init__.py
│   │   └── settings.py            ← ⚙️ TODAS LAS CONSTANTES
│   │
│   ├── 📁 scrapers/
│   │   ├── __init__.py
│   │   ├── nike.py                ← Link a scrapers/nike.py
│   │   └── sephora.py             ← Link a scrapers/sephora.py
│   │
│   ├── 📁 utils/
│   │   ├── __init__.py
│   │   └── helpers.py             ← 🛠️ FUNCIONES COMUNES
│   │
│   └── 📁 web/
│       ├── __init__.py
│       ├── app.py                 ← Flask app
│       ├── routes.py              ← Endpoints
│       ├── 📁 templates/
│       │   └── index.html
│       └── 📁 static/
│           ├── css/style.css
│           └── js/script.js
│
├── 📁 docs/                       ← 📚 DOCUMENTACIÓN
│   ├── GUIA_ESTRUCTURA.md         ← Cómo usar proyecto
│   ├── MAPA_RAPIDO.md             ← Referencia de archivos
│   ├── DESARROLLO.md              ← Guía para devs
│   ├── ESTRUCTURA_NUEVA.md        ← Cambios realizados
│   └── README_ESTRUCTURA.md       ← Este resumen
│
├── 📁 tests/                      ← ✅ TESTS
│   ├── __init__.py
│   ├── test_scrapers.py
│   └── test_api.py
│
├── 📁 scrapers/                   ← UBICACIÓN ACTUAL (aún funciona)
│   ├── nike.py
│   └── sephora.py
│
├── 📁 templates/                  ← UBICACIÓN ACTUAL
│   └── index.html
│
├── 📁 static/                     ← UBICACIÓN ACTUAL
│   ├── css/style.css
│   └── js/script.js
│
├── app.py                         ← UBICACIÓN ACTUAL
├── venv/
├── requirements.txt
├── main.py
└── README.md
```

---

## Módulos y Sus Responsabilidades

```
config/settings.py
    ├── PORCENTAJE_COSTO_CAJA
    ├── TASA_CAMBIO_GTQ
    ├── MULTIPLICADOR_PRECIO_MERCADO
    ├── PALABRAS_CLAVE_CON_TALLAS
    ├── PALABRAS_CLAVE_SIN_TALLAS
    ├── MARCAS_SOPORTADAS
    └── SELENIUM_TIMEOUT

scrapers/nike.py
    ├── scrape_nike()
    ├── scrape_nike_desde_nike_com()
    ├── scrape_nike_desde_amazon()
    ├── scrape_nike_desde_ebay()
    ├── calcular_precios()
    └── limpiar_precio()

utils/helpers.py
    ├── limpiar_precio()
    └── es_producto_con_tallas()

web/app.py
    ├── /scrape (POST)
    ├── /update (POST)
    └── routes.py (endpoints)

templates/index.html
    ├── Form marca + links
    ├── Progress bar
    └── Result container

static/
    ├── css/style.css
    └── js/script.js
```

---

## Flujo de Información

```
USUARIO
   ↓ Ingresa: Marca + Links
   ↓
FORMULARIO (JS)
   ↓ POST /scrape
   ↓
app.py (endpoint /scrape)
   ↓ Lee marca y links
   ↓
config/settings.py
   ↓ Obtiene MARCAS_SOPORTADAS
   ↓
scrapers/[marca].py
   ↓ Detecta sitio
   ↓
Scraper específico (nike_desde_amazon, etc)
   ↓ Selenium extrae datos
   ↓
utils/helpers.py
   ↓ Procesa datos
   ↓ limpiar_precio()
   ↓ es_producto_con_tallas()
   ↓
Pandas
   ↓ Crea DataFrame
   ↓ Genera Excel
   ↓
base64
   ↓ Codifica Excel
   ↓
JSON Response
   ↓ Devuelve al cliente
   ↓
JS script.js
   ↓ Pregunta si descargar
   ↓
Navegador
   ↓ Diálogo "Guardar Como..."
   ↓
USUARIO descarga archivo donde quiere
```

---

## Entrada y Salida de Datos

```
INPUT
├── Brand: "nike"
├── URLs: [
│   "https://www.nike.com/es/w/...",
│   "https://www.amazon.com/.../...",
│   "https://www.ebay.com/itm/..."
│ ]
└── Config: src/config/settings.py

PROCESSING
├── Detecta sitios
├── Ejecuta scrapers
├── Limpia datos
├── Calcula precios
└── Formatea para Excel

OUTPUT
├── Excel file
├── Columnas: Nombre | Sitio | Tallas | Precio | etc
├── Descargado por usuario
└── Guardado donde usuario elige (USB, Desktop, etc)
```

---

**Estructura implementada: 19/11/2025**
