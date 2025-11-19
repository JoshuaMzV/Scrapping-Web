# 👨‍💻 Guía para Desarrolladores

## Bienvenida

Esta guía te ayuda a entender la estructura del proyecto y cómo contribuir.

---

## 🚀 Primeros Pasos

### 1. Familiarízate con la Estructura

Lee en este orden:
1. `docs/MAPA_RAPIDO.md` - Ubicación de archivos (5 min)
2. `docs/GUIA_ESTRUCTURA.md` - Descripción completa (10 min)
3. `docs/ESTRUCTURA_NUEVA.md` - Cambios recientes (5 min)

### 2. Configura tu Entorno

```bash
# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python main.py
```

### 3. Explora el Código

- Abre `src/config/settings.py` - Entiende las constantes
- Abre `scrapers/nike.py` - Ve cómo funciona un scraper
- Abre `src/utils/helpers.py` - Funciones auxiliares disponibles

---

## 🛠️ Tareas Comunes

### Cambiar un Parámetro de Configuración

**Tarea:** Aumentar el timeout de Selenium de 20 a 30 segundos

**Pasos:**
1. Abre `src/config/settings.py`
2. Busca `SELENIUM_TIMEOUT = 20`
3. Cambia a `SELENIUM_TIMEOUT = 30`
4. Guarda el archivo

```python
# Antes
SELENIUM_TIMEOUT = 20

# Después
SELENIUM_TIMEOUT = 30
```

---

### Agregar una Nueva Constante

**Tarea:** Agregar factor de descuento adicional

**Pasos:**
1. Abre `src/config/settings.py`
2. Ve al final de la sección de configuración
3. Agrega tu constante:

```python
# Tu nueva constante
MI_NUEVO_FACTOR = 1.15
```

4. Importa en tu código:
```python
from src.config import MI_NUEVO_FACTOR
```

---

### Agregar una Función Auxiliar

**Tarea:** Crear función para formatear números

**Pasos:**
1. Abre `src/utils/helpers.py`
2. Agrega tu función:

```python
def formatear_numero(numero, decimales=2):
    """Formatea un número a dos decimales"""
    return f"{numero:.{decimales}f}"
```

3. Exporta en `src/utils/__init__.py`:

```python
from .helpers import formatear_numero
```

4. Úsalo en tu código:

```python
from src.utils import formatear_numero
resultado = formatear_numero(123.456)  # "123.46"
```

---

### Modificar un Scraper

**Tarea:** Cambiar selector de precio en Nike

**Pasos:**
1. Abre `scrapers/nike.py`
2. Busca la función `scrape_nike_desde_amazon()`
3. Localiza donde extrae el precio
4. Prueba nuevos selectores:

```python
# Antes
precio_elem = driver.find_element(By.CSS_SELECTOR, '.a-price')

# Después (ejemplo)
precio_elem = driver.find_element(By.CSS_SELECTOR, '[data-a-color="price"]')
```

5. Prueba cambios con `python -c "from scrapers.nike import scrape_nike_desde_amazon; ..."`

---

### Agregar Soporte para Nueva Marca

**Tarea:** Agregar soporte para Adidas

**Pasos:**

#### 1. Crear nuevo scraper
- Crea `scrapers/adidas.py` con función `scrape_adidas(driver, wait, url)`
- Implementa detección de sitios (Adidas.com, Amazon, eBay)
- Extrae nombre, precio, imagen, tallas

#### 2. Registrar marca en config
```python
# src/config/settings.py
MARCAS_SOPORTADAS = {
    'nike': 'Nike',
    'sephora': 'Sephora',
    'adidas': 'Adidas'  # Agregar esta línea
}
```

#### 3. Agregar palabras clave
```python
# src/config/settings.py
PALABRAS_CLAVE_CON_TALLAS.extend(['adidas', 'boost', 'ultraboost'])
```

#### 4. Actualizar interfaz web
- Abre `templates/index.html`
- Busca el `<select id="marca">`
- Agrega: `<option value="adidas">👟 Adidas</option>`

#### 5. Actualizar app.py
```python
# En app.py, función scrape()
elif 'adidas' in marca.lower():
    scraper_func = scrape_adidas
    calcular = adidas_calcular
```

---

## 📝 Convenciones de Código

### Nombres de Funciones
```python
# ❌ Evitar
def obtenerPrecio(url):
    pass

# ✅ Preferir
def obtener_precio(url):
    pass
```

### Documentación
```python
# ✅ Incluir docstrings
def limpiar_precio(precio_str):
    """
    Limpia un string de precio y retorna float
    
    Args:
        precio_str (str): String con precio, ej: "US$123.45"
        
    Returns:
        float: Precio como número, ej: 123.45
    """
    return float(precio_str.replace('$', ''))
```

### Variables
```python
# ✅ Nombres claros
timeout_selenium = 20
palabras_clave = ['nike', 'adidas']

# ❌ Evitar
t = 20
pk = ['nike', 'adidas']
```

---

## 🧪 Escribir Tests

### Test de Scraper

```python
# tests/test_scrapers.py
from scrapers.nike import scrape_nike_desde_nike_com

def test_scraper_nike_valida_estructura():
    """Verifica que scraper retorna estructura correcta"""
    resultado = scrape_nike_desde_nike_com(driver, wait, url)
    
    # Verificar campos obligatorios
    assert 'nombre' in resultado
    assert 'precio' in resultado
    assert 'tallas' in resultado
    assert 'sitio' in resultado
    
    # Verificar tipos
    assert isinstance(resultado['nombre'], str)
    assert resultado['nombre'] != ''
```

### Ejecutar Tests

```bash
# Instalar pytest
pip install pytest

# Ejecutar todos
pytest tests/

# Ejecutar uno específico
pytest tests/test_scrapers.py::test_scraper_nike_valida_estructura

# Con verbose
pytest -v tests/
```

---

## 🐛 Debugging

### Agregar Logs

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Iniciando scraping")
logger.debug(f"URL: {url}")
logger.error("Error al extraer precio")
```

### Usar Breakpoint

```python
# Python 3.7+
def mi_funcion():
    x = 5
    breakpoint()  # Pausa aquí
    return x * 2
```

### Inspeccionar Página con Selenium

```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get("https://example.com")

# Ver HTML
print(driver.page_source)

# Ver elemento específico
elem = driver.find_element(By.ID, "myid")
print(elem.get_attribute('outerHTML'))
```

---

## 📚 Recursos Útiles

- [Documentación Selenium](https://www.selenium.dev/documentation/)
- [Documentación Pandas](https://pandas.pydata.org/docs/)
- [Documentación Flask](https://flask.palletsprojects.com/)
- [CSS Selectors](https://developer.mozilla.org/es/docs/Web/CSS/Selectors)

---

## 💬 Preguntas Frecuentes

### P: ¿Dónde agrego una nueva constante?
**R:** `src/config/settings.py`

### P: ¿Cómo pruebo un scraper?
**R:** Crea un archivo en `tests/` o usa `pytest`

### P: ¿Cómo cambio el puerto de Flask?
**R:** `src/config/settings.py` - cambiar `FLASK_PORT`

### P: ¿Se puede agregar otra marca fácilmente?
**R:** Sí, sigue los pasos en "Agregar Soporte para Nueva Marca"

---

**Última actualización:** 19/11/2025
**Preguntas:** Revisar `docs/` o consultar código existente
