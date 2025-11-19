# 📦 Estructura de Proyecto - Catálogo Generator

## 📋 Descripción General

Este proyecto utiliza una estructura **profesional y escalable** que permite a cualquier desarrollador entender rápidamente dónde se encuentra cada componente.

---

## 📂 Estructura de Carpetas

```
scraping_project/
│
├── src/                              # 🔧 Código fuente principal
│   ├── config/                       # ⚙️ Configuración centralizada
│   │   ├── __init__.py
│   │   └── settings.py               # Variables de configuración global
│   │
│   ├── scrapers/                     # 🕷️ Lógica de scraping por marca
│   │   ├── __init__.py
│   │   ├── nike.py                   # Scraper Nike (Nike.com, Amazon, eBay)
│   │   └── sephora.py                # Scraper Sephora
│   │
│   ├── utils/                        # 🛠️ Funciones auxiliares
│   │   ├── __init__.py
│   │   └── helpers.py                # Funciones comunes (precios, tallas, etc.)
│   │
│   └── web/                          # 🌐 Interfaz web Flask
│       ├── app.py                    # Aplicación principal Flask
│       ├── routes.py                 # Rutas HTTP
│       ├── templates/                # Plantillas HTML
│       │   └── index.html            # Página principal
│       └── static/                   # Archivos estáticos
│           ├── css/
│           │   └── style.css         # Estilos
│           └── js/
│               └── script.js         # Lógica JavaScript del cliente
│
├── docs/                             # 📚 Documentación
│   ├── GUIA_ESTRUCTURA.md            # Este archivo
│   ├── API.md                        # Documentación de endpoints
│   ├── DESARROLLO.md                 # Guía para desarrolladores
│   └── CAMBIOS.md                    # Registro de cambios
│
├── tests/                            # ✅ Tests y pruebas
│   ├── __init__.py
│   ├── test_scrapers.py              # Tests de scrapers
│   └── test_api.py                   # Tests de endpoints
│
├── venv/                             # 🐍 Entorno virtual Python
│
├── requirements.txt                  # Dependencias del proyecto
├── main.py                           # Script de entrada principal
└── README.md                         # Readme del proyecto
```

---

## 🎯 Cómo Navegar por el Proyecto

### 📝 Modificar Configuración Global
**Archivo:** `src/config/settings.py`

Aquí encontrarás:
- Variables de configuración (puertos, timeouts, etc.)
- Palabras clave para detección de productos
- Constantes de precios y cálculos

```python
# Ejemplo: cambiar timeout de Selenium
SELENIUM_TIMEOUT = 30  # Aumentar de 20 a 30 segundos
```

---

### 🕷️ Agregar un Nuevo Scraper
**Directorio:** `src/scrapers/`

1. Crear archivo `mi_marca.py` en `src/scrapers/`
2. Implementar función `scrape_mi_marca(driver, wait, url)`
3. Registrar en `src/scrapers/__init__.py`

```python
# Estructura básica de un scraper
def scrape_mi_marca(driver, wait, url):
    driver.get(url)
    nombre = driver.find_element(By.ID, "productTitle").text
    precio = extraer_precio(driver)
    tallas = extraer_tallas(driver)
    
    return {
        "nombre": nombre,
        "precio": precio,
        "tallas": tallas,
        "sitio": "Mi Marca"
    }
```

---

### 🛠️ Agregar Funciones Auxiliares
**Archivo:** `src/utils/helpers.py`

Aquí van funciones reutilizables:
- Limpieza de precios
- Conversión de monedas
- Detección de tipos de producto

```python
def mi_funcion_nueva(parametro):
    """Descripción de qué hace"""
    # Tu código aquí
    return resultado
```

---

### 🌐 Modificar la Interfaz Web
**Archivos:**
- `src/web/templates/index.html` - Estructura HTML
- `src/web/static/css/style.css` - Estilos
- `src/web/static/js/script.js` - Lógica del cliente
- `src/web/routes.py` - Endpoints del servidor

---

### 🔌 Agregar Nuevos Endpoints API
**Archivo:** `src/web/routes.py`

```python
@app.route('/api/mi_endpoint', methods=['POST'])
def mi_endpoint():
    data = request.get_json()
    # Tu lógica aquí
    return jsonify({'success': True})
```

---

### ✅ Escribir Tests
**Directorio:** `tests/`

```python
# tests/test_scrapers.py
def test_scraper_nike():
    resultado = scrape_nike_desde_nike_com(driver, wait, url)
    assert resultado['nombre'] is not None
    assert resultado['precio'] != 'Error'
```

---

## 📚 Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `src/config/settings.py` | Configuración global |
| `src/scrapers/nike.py` | Lógica de extracción Nike |
| `src/utils/helpers.py` | Funciones comunes |
| `src/web/app.py` | Aplicación Flask |
| `docs/API.md` | Documentación de endpoints |
| `requirements.txt` | Dependencias Python |

---

## 🚀 Iniciando el Proyecto

```bash
# 1. Activar entorno virtual
.\venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar aplicación
python main.py
```

---

## 💡 Ejemplos de Tareas Comunes

### Cambiar el formato de salida del Excel
**Archivo:** `src/web/app.py` - Sección de generación de Excel

### Agregar soporte para una nueva marca
**Pasos:**
1. Crear `src/scrapers/mi_marca.py`
2. Implementar función `scrape_mi_marca()`
3. Registrar en `src/config/settings.py` (MARCAS_SOPORTADAS)
4. Actualizar `src/web/templates/index.html` (agregar opción al select)

### Cambiar los cálculos de precio
**Archivo:** `src/config/settings.py`

Buscar variables de cálculo:
- `PORCENTAJE_COSTO_CAJA`
- `MULTIPLICADOR_PRECIO_MERCADO`
- Etc.

---

## 📞 Contacto & Soporte

Para dudas sobre la estructura o implementación:
- Revisar `docs/DESARROLLO.md`
- Consultar archivos de configuración (settings.py)
- Revisar ejemplos en scrapers existentes

---

**Última actualización:** 19/11/2025
