# 🗺️ MAPA RÁPIDO DE ARCHIVOS

## ¿Qué quiero hacer? → ¿Dónde voy?

### 🔧 Cambiar Configuración
- Portos, hosts → `src/config/settings.py`
- Constantes de precios → `src/config/settings.py`
- Palabras clave de detección → `src/config/settings.py`
- Marca soportada → `src/config/settings.py`

### 🕷️ Modificar Scraping
- Cambiar extracción Nike → `scrapers/nike.py` (o `src/scrapers/nike.py`)
- Cambiar extracción Sephora → `scrapers/sephora.py` (o `src/scrapers/sephora.py`)
- Agregar nueva marca → Crear `scrapers/nueva.py` + registrar en `settings.py`

### 🛠️ Funciones Auxiliares
- Limpiar precios → `src/utils/helpers.py`
- Detectar tallas → `src/utils/helpers.py`
- Función nueva común → `src/utils/helpers.py`

### 🌐 Interfaz Web
- HTML/estructura → `templates/index.html` (o `src/web/templates/`)
- Estilos CSS → `static/css/style.css` (o `src/web/static/css/`)
- JavaScript → `static/js/script.js` (o `src/web/static/js/`)
- Endpoints HTTP → `app.py` (o `src/web/routes.py`)

### 📚 Documentación
- Guía de estructura → `docs/GUIA_ESTRUCTURA.md`
- Explicación nueva estructura → `docs/ESTRUCTURA_NUEVA.md`
- Mapa rápido → `docs/MAPA_RAPIDO.md` (este archivo)

### ✅ Tests
- Tests de scrapers → `tests/test_scrapers.py`
- Tests de API → `tests/test_api.py`

---

## 📞 Ubicación Actual vs Nueva

| Componente | Ubicación Actual | Ubicación Nueva |
|-----------|-----------------|-----------------|
| Scrapers | `scrapers/` | `src/scrapers/` |
| Templates | `templates/` | `src/web/templates/` |
| Static | `static/` | `src/web/static/` |
| App Flask | `app.py` | `src/web/app.py` |
| Config | (esparcida) | `src/config/settings.py` |
| Helpers | (esparcida) | `src/utils/helpers.py` |

**Estado:** ✅ Estructuras nuevas creadas, ubicaciones antiguas aún funcionan

---

**Última actualización:** 19/11/2025
