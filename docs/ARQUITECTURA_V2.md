# 🏗️ Arquitectura del Sistema - Refactorizada por Marca

## 📐 Diagrama de Flujo

```
┌─────────────────────────────────────────────────────────────┐
│                    USUARIO FINAL                            │
│            (Abre iniciar.bat o python run.py)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              WEB INTERFACE (Flask)                          │
│            http://127.0.0.1:5000                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ • Selector de Marca (Nike, Sephora)               │  │
│  │ • Textarea para URLs (cualquier sitio)            │  │
│  │ • Botón "Generar Catálogo"                        │  │
│  │ • Barra de progreso                               │  │
│  └─────────────────────────────────────────────────────┘  │
└────────┬──────────────────────────────────────────────────┘
         │
         │ AJAX POST /scrape
         │ {marca: "nike", links: [...]}
         │
         ↓
┌─────────────────────────────────────────────────────────────┐
│            BACKEND (app.py)                                │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 1. Recibe marca + links                            │  │
│  │ 2. Selecciona scraper según marca                  │  │
│  │    if marca == "nike": scraper = scrape_nike       │  │
│  │    if marca == "sephora": scraper = scrape_sephora │  │
│  │ 3. Llama scraper con cada URL                      │  │
│  │ 4. Scraper detecta sitio automáticamente           │  │
│  │ 5. Procesa datos y calcula precios                 │  │
│  │ 6. Genera Excel                                    │  │
│  │ 7. Retorna URL de descarga                         │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────┬──────────────────────────────────────────────────┘
          │
          ├─────────────────┬──────────────────┬─────────────────┐
          │                 │                  │                 │
          ↓                 ↓                  ↓                 ↓
    ┌──────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐
    │ SCRAPERS │    │ SCRAPERS     │    │ SCRAPERS     │    │ UTILS    │
    │          │    │              │    │              │    │          │
    │ nike.py  │    │ sephora.py   │    │ amazon.py    │    │ limpiar_ │
    │          │    │              │    │ (futuro)     │    │ precio() │
    │ ┌──────┐ │    │ ┌──────────┐ │    │ ┌──────────┐ │    │ calcular │
    │ │nike. │ │    │ │sephora.  │ │    │ │amazon.   │ │    │ _precios │
    │ │com   │ │    │ │com       │ │    │ │com       │ │    │          │
    │ └──────┘ │    │ └──────────┘ │    │ └──────────┘ │    └──────────┘
    │ ┌──────┐ │    │ ┌──────────┐ │    │ ┌──────────┐ │
    │ │amazon │ │    │ │amazon    │ │    │ │alibaba   │ │
    │ └──────┘ │    │ └──────────┘ │    │ │(futuro)  │ │
    │ ┌──────┐ │    │ ┌──────────┐ │    │ └──────────┘ │
    │ │ebay  │ │    │ │ebay      │ │
    │ └──────┘ │    │ └──────────┘ │
    └──────────┘    └──────────────┘
          │                 │
          └────────┬────────┘
                   │
         ┌─────────↓──────────┐
         │ SELENIUM BROWSER   │
         │ • ChromeDriver     │
         │ • WebDriverWait    │
         └────────┬───────────┘
                  │
                  ↓
         ┌─────────────────────────┐
         │ WEB PAGES               │
         │ • Nike.com              │
         │ • Amazon.com            │
         │ • eBay.com              │
         │ • Sephora.com           │
         │ • (Más en futuro)       │
         └────────┬────────────────┘
                  │
                  ↓
         ┌─────────────────────────┐
         │ PANDAS DataFrame        │
         │ • Procesa datos         │
         │ • Ordena columnas       │
         │ • Formatea valores      │
         └────────┬────────────────┘
                  │
                  ↓
         ┌─────────────────────────┐
         │ EXCEL (openpyxl)        │
         │ catalogo_nike_...xlsx   │
         └────────┬────────────────┘
                  │
                  ↓
         ┌─────────────────────────┐
         │ DOWNLOADS FOLDER        │
         │ C:\Users\...\Downloads\ │
         └─────────────────────────┘
```

---

## 📁 Estructura de Directorios

```
scraping_project/
├── app.py                          # Backend Flask (250 líneas)
├── run.py                          # Launcher del servidor
├── requirements.txt                # Dependencias Python
│
├── templates/
│   └── index.html                  # Interfaz web (152 líneas)
│
├── static/
│   ├── css/
│   │   └── style.css              # Estilos (390+ líneas)
│   └── js/
│       └── script.js              # Lógica frontend (150+ líneas)
│
├── scrapers/                       # Módulo de scrapers
│   ├── __init__.py
│   ├── nike.py                     # Marca: Nike (múltiples sitios)
│   ├── sephora.py                  # Marca: Sephora (múltiples sitios)
│   └── amazon.py                   # Futuro: Marca Amazon
│
├── venv/                           # Entorno virtual Python
│   └── ...
│
├── iniciar.bat                     # Launcher Windows (CMD)
├── iniciar.ps1                     # Launcher Windows (PowerShell)
├── build_exe.py                    # Constructor de .exe
│
├── README.md                       # Documentación principal
├── ESTRUCTURA.md                   # Detalles técnicos
├── CAMBIOS.md                      # Qué se modificó
├── RESUMEN_CAMBIOS.md             # Comparativa antes/después
└── GUIA_USO.md                     # Manual de usuario

venv/                               # Entorno aislado
├── Scripts/
│   └── python.exe, pip.exe, etc.
├── Lib/
│   └── site-packages/
│       ├── selenium/
│       ├── pandas/
│       ├── flask/
│       ├── openpyxl/
│       └── ...
```

---

## 🔄 Flujo de Datos Detallado

### 1. Usuario Selecciona Marca

**Input:**
```javascript
marca = "nike"
links = [
  "https://nike.com/...",
  "https://amazon.com/...",
  "https://ebay.com/..."
]
```

**Envío al backend:**
```javascript
POST /scrape
{
  "marca": "nike",
  "links": [...]
}
```

### 2. Backend Identifica Scraper

```python
# app.py - línea ~95
if 'nike' in marca.lower():
    scraper_func = scrape_nike
    calcular = nike_calcular
elif 'sephora' in marca.lower():
    scraper_func = scrape_sephora
    calcular = sephora_calcular
```

### 3. Scraper Detecta Sitio

```python
# scrapers/nike.py - línea ~75
def scrape_nike(driver, wait, url):
    print(f"🔍 Detectando sitio...", end="")
    
    if "nike.com" in url.lower():
        print(" Nike.com")
        return scrape_nike_desde_nike_com(driver, wait, url)
    elif "amazon" in url.lower():
        print(" Amazon")
        return scrape_nike_desde_amazon(driver, wait, url)
    elif "ebay" in url.lower():
        print(" eBay")
        return scrape_nike_desde_ebay(driver, wait, url)
```

### 4. Scraper Específico Extrae Datos

Ejemplo Nike.com:
```python
def scrape_nike_desde_nike_com(driver, wait, url):
    driver.get(url)
    nombre = driver.find_element(By.ID, "pdp_product_title").text
    precio_str = driver.find_element(By.CSS_SELECTOR, '[data-testid="currentPrice-container"]').text
    imagen = driver.find_element(By.CSS_SELECTOR, 'img[src^="https://static.nike.com"]').get_attribute('src')
    
    return {
        "nombre": nombre,
        "precio": precio_str,
        "imagen": imagen,
        "tallas": tallas,
        "sitio": "Nike.com"  # ← Etiqueta el sitio
    }
```

Ejemplo Amazon:
```python
def scrape_nike_desde_amazon(driver, wait, url):
    driver.get(url)
    nombre = driver.find_element(By.ID, "productTitle").text
    precio_str = driver.find_element(By.CSS_SELECTOR, 'span.aok-offscreen').text
    
    return {
        "nombre": nombre,
        "precio": precio_str,
        "imagen": imagen,
        "tallas": tallas,
        "sitio": "Amazon"  # ← Etiqueta diferente
    }
```

### 5. Backend Procesa y Calcula

```python
# app.py - línea ~115
for url in links:
    datos = scraper_func(driver, wait, url)
    
    if datos:
        precio_usd = limpiar_precio(datos['precio'])
        precios = calcular(precio_usd)  # Calcula costos
        
        row = {
            'Nombre del Producto': datos['nombre'],
            'Sitio': datos['sitio'],  # ← Información de dónde vino
            'Tallas Disponibles': datos.get('tallas'),
            'URL Imagen': datos.get('imagen'),
            'URL Producto': url,
            **precios  # Expande diccionario de precios
        }
        datos_encontrados.append(row)
```

### 6. Genera Excel

```python
# app.py - línea ~140
df = pd.DataFrame(datos_encontrados)
filename = f"catalogo_nike_{datetime_stamp}.xlsx"
filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
df.to_excel(filepath, index=False)
```

### 7. Retorna URL de Descarga

```python
return jsonify({
    'success': True,
    'message': f'Catálogo con {len(datos_encontrados)} productos',
    'filename': filename
})
```

### 8. Frontend Descarga Automáticamente

```javascript
// static/js/script.js
fetch('/download/' + filename)
  .then(response => response.blob())
  .then(blob => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
  });
```

---

## 🔌 Puntos de Extensión

### Agregar Nuevo Sitio (para marca existente)

**Ubicación:** `scrapers/[marca].py`

```python
def scrape_nike_desde_alibaba(driver, wait, url):
    """Nueva función específica"""
    driver.get(url)
    # Implementar selectors de Alibaba
    return {...}

def scrape_nike(driver, wait, url):
    # Agregar rama
    elif "alibaba" in url.lower():
        return scrape_nike_desde_alibaba(driver, wait, url)
```

**Cambios necesarios:** Solo en el scraper. `app.py` NO necesita cambios.

### Agregar Nueva Marca

**Paso 1:** Crear `scrapers/[nueva_marca].py`
```python
def scrape_adidas(driver, wait, url):
    if "adidas.com" in url.lower(): ...
    elif "amazon" in url.lower(): ...
    elif "ebay" in url.lower(): ...
```

**Paso 2:** Actualizar `app.py`
```python
from scrapers.adidas import scrape_adidas, calcular_precios as adidas_calcular

if 'adidas' in marca.lower():
    scraper_func = scrape_adidas
    calcular = adidas_calcular
```

**Paso 3:** Actualizar `templates/index.html`
```html
<option value="adidas">👟 Adidas (links de...)</option>
```

---

## ⚡ Flujos Críticos

### Flujo 1: Manejo de Errores
```
Usuario pega URL ❌
    ↓
Scraper intenta abrir en navegador
    ↓
Timeout o elemento no encontrado
    ↓
Función retorna None o {"nombre": "Error"}
    ↓
Backend detecta error
    ↓
Salta al siguiente URL
    ↓
Continúa con los siguientes
    ↓
Genera Excel solo con los que sí funcionaron
```

### Flujo 2: Cierre de Pop-ups (Nike.com)
```
Abre Nike.com
    ↓
Busca pop-ups con CSS selectors
    ↓
Intenta cerrar hasta 3 veces
    ↓
Espera elemento clave
    ↓
Si existe: extrae datos ✅
Si no existe: error manejado ❌
```

### Flujo 3: Detección de Tallas
```
Intenta selector Nike
    ↓
No encontrado: fallback a Amazon
    ↓
No encontrado: fallback a genérico
    ↓
No encontrado: retorna "No encontradas"
```

---

## 📊 Ejemplo de Transformación de Datos

### Entrada (Raw Data)
```python
{
    "nombre": "Nike Air Force 1 '07",
    "precio": "$110.00",
    "imagen": "https://static.nike.com/...",
    "tallas": "6, 7, 8, 9",
    "sitio": "Nike.com"
}
```

### Procesamiento (calcular_precios)
```python
precio_usd = 110.00

costo_caja = 110 * 0.08 = 8.80
costo_envio = 110 * 0.05 = 5.50
subtotal = 110 + 8.80 + 5.50 = 124.30
costo_seguro = 124.30 * 0.03 = 3.73
costo_final_usd = 124.30 + 3.73 = 128.03

precio_mercado_gtq = (110 * 1.40) * 7.8 = 1202.40
precio_venta_gtq = 1202.40 * 0.90 = 1082.16

costo_final_gtq = 128.03 * 7.8 = 998.63
ganancia_gtq = 1082.16 - 998.63 = 83.53
margen = (83.53 / 1082.16) * 100 = 7.72%
```

### Salida (Excel)
```
Nombre | Sitio | Precio | Costo USD | Costo GTQ | Venta GTQ | Ganancia | Margen
Nike AF1 | Nike.com | 110.00 | 128.03 | 998.63 | 1082.16 | 83.53 | 7.72%
```

---

## 🔐 Seguridad

- ✅ **Todo local:** No hay conexiones externas (salvo GitHub para actualizar)
- ✅ **Sin credenciales:** No se requieren logins
- ✅ **Sin bases de datos:** Archivos Excel locales
- ✅ **Ejecutable aislado:** La .exe no accede a archivos del sistema
- ✅ **User-agent personalizado:** Evita detectores de bots

---

## 🎯 Resumen de Cambios desde v1

| Aspecto | v1 (Monolítico) | v2 (Modular) |
|---------|---|---|
| Estructura | 1 archivo scrape_nike.py | 3 scrapers separados |
| Sitios soportados | Solo Nike.com | Nike.com + Amazon + eBay |
| Decisión | En app.py (URL → scraper) | En scraper (URL → extractor) |
| Extensibilidad | Compleja (modificar app.py) | Simple (agregar función) |
| UX | Confusa (¿marca o sitio?) | Clara (solo marca) |
| Archivos | Múltiples por ejecución | 1 por marca |

