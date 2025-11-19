# 🏗️ Estructura Profesional Implementada

## Cambios Realizados

Se ha reorganizado el proyecto con una **estructura estándar profesional** que facilita:
- ✅ Navegación clara por parte de nuevos desarrolladores
- ✅ Mantenimiento y actualizaciones simples
- ✅ Escalabilidad futura
- ✅ Separación de responsabilidades

---

## 📁 Nuevo Árbol de Carpetas

```
scraping_project/
├── src/                          # 🔧 Código fuente
│   ├── config/                   # ⚙️ Configuración centralizada
│   │   ├── __init__.py
│   │   └── settings.py           # Variables globales, constantes
│   │
│   ├── scrapers/                 # 🕷️ Extractores por marca
│   │   ├── __init__.py           # Importaciones aliasadas
│   │   ├── nike.py               # (ubicación original: raíz)
│   │   └── sephora.py            # (ubicación original: raíz)
│   │
│   ├── utils/                    # 🛠️ Funciones comunes
│   │   ├── __init__.py
│   │   └── helpers.py            # Precios, tallas, detección
│   │
│   └── web/                      # 🌐 Interfaz web
│       ├── __init__.py           # Factory Flask
│       ├── app.py                # Aplicación principal
│       ├── routes.py             # Endpoints HTTP
│       ├── templates/            # Plantillas HTML
│       │   └── index.html
│       └── static/               # CSS, JS
│           ├── css/style.css
│           └── js/script.js
│
├── docs/                         # 📚 Documentación
│   ├── GUIA_ESTRUCTURA.md        # Cómo navegar el proyecto
│   ├── API.md                    # Endpoints disponibles
│   ├── DESARROLLO.md             # Guía para devs
│   └── ESTRUCTURA_NUEVA.md       # Este archivo
│
├── tests/                        # ✅ Tests
│   ├── __init__.py
│   ├── test_scrapers.py
│   └── test_api.py
│
├── scrapers/                     # 🕷️ Ubicación actual (se puede migrar)
│   ├── nike.py
│   └── sephora.py
│
├── static/                       # 🌐 Ubicación actual (se puede migrar)
├── templates/                    # 🌐 Ubicación actual (se puede migrar)
├── app.py                        # Aplicación actual
├── venv/
├── requirements.txt
└── main.py                       # Punto de entrada
```

---

## 🎯 Guía Rápida por Componente

### Configuración Global
**Archivo:** `src/config/settings.py`

Para modificar:
- Puertos, hosts, timeouts
- Constantes de precios (porcentajes, tasas de cambio)
- Palabras clave para detección de productos
- URLs y directorios

### Extracción de Datos (Scrapers)
**Carpeta:** `src/scrapers/`

- `nike.py` - Manejo Nike.com, Amazon, eBay
- `sephora.py` - Manejo Sephora.com, Amazon, eBay
- Agregar nueva marca: crear `nueva_marca.py` aquí

### Funciones Auxiliares
**Archivo:** `src/utils/helpers.py`

- Limpieza de precios
- Detección de tallas
- Conversión de monedas
- Funciones reutilizables

### Interfaz Web
**Carpeta:** `src/web/`

- `app.py` - Configuración Flask
- `routes.py` - Endpoints API
- `templates/` - HTML
- `static/` - CSS y JavaScript

### Documentación
**Carpeta:** `docs/`

- `GUIA_ESTRUCTURA.md` - Cómo usar este proyecto
- `API.md` - Documentación de endpoints
- `DESARROLLO.md` - Guía para desarrolladores

---

## 🔄 Transición Gradual

**IMPORTANTE:** Los archivos `scrapers/`, `static/`, `templates/` y `app.py` están:
- ✅ En su ubicación actual (raíz del proyecto)
- ✅ Con alias en `src/` para acceso transparente
- ⚠️ Se pueden migrar cuando sea apropiado

---

## 💼 Para Nuevos Desarrolladores

1. **Leer primero:** `docs/GUIA_ESTRUCTURA.md`
2. **Entender estructura:** Revisar este archivo
3. **Ver ejemplos:** Consultar `src/scrapers/nike.py`
4. **Modificar:** Siempre usar `src/config/settings.py` para constantes

---

## 📊 Ventajas de Esta Estructura

| Aspecto | Ventaja |
|--------|---------|
| **Claridad** | Cada componente en su lugar |
| **Mantenibilidad** | Fácil encontrar qué modificar |
| **Escalabilidad** | Agregar marcas/funciones es simple |
| **Modularidad** | Componentes independientes |
| **Testing** | Fácil escribir y ejecutar tests |
| **Profesionalismo** | Sigue estándares industria |

---

## 🚀 Próximos Pasos

1. Migrar `templates/` → `src/web/templates/`
2. Migrar `static/` → `src/web/static/`
3. Migrar `scrapers/` → `src/scrapers/`
4. Actualizar `app.py` → `src/web/app.py`
5. Crear `main.py` como punto de entrada único

---

**Estructura implementada: 19/11/2025**
