# 📋 ESTRUCTURA DEL PROYECTO - Generador de Catálogos

## 🎯 Descripción General

Aplicación escalable para generar catálogos de productos desde múltiples tiendas en línea. Incluye interfaz web moderna, sistema de scraping modular y auto-actualización desde GitHub.

---

## 📁 Estructura de Carpetas

```
scraping_project/
│
├── 📄 app.py                    ← Backend principal (Flask)
├── 📄 run.py                    ← Script para ejecutar la app
├── 📄 build_exe.py              ← Script para crear .exe
├── 📄 iniciar.bat               ← Atajo para Windows (CMD)
├── 📄 iniciar.ps1               ← Atajo para Windows (PowerShell)
├── 📄 requirements.txt           ← Dependencias Python
├── 📄 README.md                 ← Documentación
│
├── 📁 templates/                ← HTML de la interfaz
│   └── 📄 index.html            ← Página principal
│
├── 📁 static/                   ← Archivos estáticos
│   ├── 📁 css/
│   │   └── 📄 style.css         ← Estilos CSS
│   └── 📁 js/
│       └── 📄 script.js         ← Lógica frontend
│
├── 📁 scrapers/                 ← Módulos de scraping
│   ├── 📄 __init__.py           ← Inicializador
│   ├── 📄 nike.py               ← Scraper Nike
│   └── 📄 sephora.py            ← Scraper Sephora
│
├── 📁 venv/                     ← Entorno virtual Python
│
└── 📁 dist/                     ← (Se crea) Ejecutable .exe
```

---

## 🚀 Cómo Usar

### Opción 1: Ejecutable (.exe) - Recomendado para el encargado

1. **Hacer doble clic en `CatalogoGenerator.exe`**
2. Se abrirá la interfaz automáticamente
3. Pegar links
4. Generar catálogo
5. Descargar Excel

### Opción 2: Desde Python (Desarrollo)

```bash
# Opción A: Con script .bat (Windows CMD)
iniciar.bat

# Opción B: Con script .ps1 (Windows PowerShell)
.\iniciar.ps1

# Opción C: Manual
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

---

## 📝 Archivos Principales

### `app.py` - Backend Flask
- ✅ Maneja rutas HTTP
- ✅ Procesa solicitudes de scraping
- ✅ Genera Excel automáticamente
- ✅ Gestiona actualizaciones desde GitHub
- ✅ Servir archivos estáticos

### `run.py` - Ejecutor de la App
- ✅ Inicia Flask en localhost:5000
- ✅ Abre navegador automáticamente
- ✅ Manejo de excepciones

### `build_exe.py` - Constructor de Ejecutable
- ✅ Convierte Python a .exe con PyInstaller
- ✅ Empaqueta templates, static y scrapers
- ✅ Genera ejecutable de un solo archivo

### `templates/index.html` - Interfaz Web
- ✅ NavBar con opciones
- ✅ Selector de marca
- ✅ Textarea para pegar links
- ✅ Botón de generar catálogo
- ✅ Sección de configuración
- ✅ Actualización desde GitHub

### `static/css/style.css` - Estilos
- ✅ Diseño moderno y responsivo
- ✅ Gradientes purpura
- ✅ Animaciones suaves
- ✅ Mobile friendly

### `static/js/script.js` - Lógica Frontend
- ✅ Navegación entre secciones
- ✅ Comunicación con backend (AJAX)
- ✅ Manejo de progreso
- ✅ Descargas automáticas

### `scrapers/nike.py` - Scraper de Nike
- ✅ Extrae nombre, precio, imagen, tallas
- ✅ Cierra pop-ups automáticamente
- ✅ Calcula precios y ganancias
- ✅ Formato escalable

### `scrapers/sephora.py` - Scraper de Sephora
- ✅ Similar a Nike
- ✅ Adaptado para Sephora.com
- ✅ Mismo formato de datos

---

## 🔧 Cómo Agregar Nueva Marca

### Paso 1: Crear scraper

Crear `scrapers/adidas.py`:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

def scrape_adidas(driver, wait, url):
    """Scraper para Adidas"""
    try:
        driver.get(url)
        # Tu lógica aquí
        nombre = driver.find_element(By.CSS_SELECTOR, '.titulo').text
        precio = driver.find_element(By.CSS_SELECTOR, '.precio').text
        # ... más extracción
        return {"nombre": nombre, "precio": precio, "imagen": imagen, "tallas": tallas}
    except Exception as e:
        return {"nombre": "Error", ...}

def calcular_precios(precio_usd):
    # Misma lógica de cálculo
    ...
```

### Paso 2: Actualizar `app.py`

En función `scrape()`, agregar:

```python
elif 'adidas' in marca.lower():
    from scrapers.adidas import scrape_adidas, calcular_precios as adidas_calcular
    datos_extraidos = scrape_adidas(driver, wait, url)
    calcular = adidas_calcular
```

### Paso 3: Actualizar `index.html`

En selector de marcas:

```html
<option value="adidas">👟 Adidas</option>
```

### Paso 4: Actualizar marcas en sección de INFO

Agregar tarjeta en `#marcas`:

```html
<div class="marca-card">
    <h3>👟 Adidas</h3>
    <p>Scraping de productos Adidas</p>
    <span class="badge">Activo</span>
</div>
```

---

## 📦 Dependencias

```
pandas          - Procesamiento de datos
selenium        - Web scraping
webdriver-manager - Gestión automática de ChromeDriver
flask           - Servidor web
openpyxl        - Generación de Excel
requests        - HTTP requests
beautifulsoup4  - Parseo HTML
```

---

## ⚙️ Configuración de Precios

En `scrapers/nike.py` y `scrapers/sephora.py`:

```python
PORCENTAJE_COSTO_CAJA = 8.0      # Costo de empaque (%)
PORCENTAJE_COSTO_ENVIO = 5.0     # Costo de envío (%)
PORCENTAJE_SEGURO = 3.0          # Seguro (%)
TASA_CAMBIO_GTQ = 7.8            # Tipo de cambio USD → GTQ
MULTIPLICADOR_PRECIO_MERCADO = 1.40  # Margen de mercado
FACTOR_DESCUENTO_VENTA = 0.90    # Descuento en venta
```

---

## 🔄 Sistema de Actualización

### Cómo Funciona

1. Usuario ingresa URL de GitHub: `https://github.com/usuario/repo`
2. Haz clic en "Actualizar Ahora"
3. La app clona el repositorio
4. Extrae archivos modificados
5. Reemplaza archivos locales
6. Limpia archivos temporales
7. Usuario reinicia la app

### Esto requiere:
- Git instalado en la PC
- Repositorio GitHub público

---

## 🏗️ Crear Ejecutable (.exe)

```bash
# Paso 1: Instalar PyInstaller
pip install pyinstaller

# Paso 2: Ejecutar script de build
python build_exe.py

# Paso 3: El .exe estará en:
# dist/CatalogoGenerator.exe
```

### Distribución

- Copiar solo `dist/CatalogoGenerator.exe`
- El usuario no necesita Python
- No necesita instalar dependencias
- Funciona 100% local

---

## 📊 Flujo de Datos

```
Usuario escribe links
         ↓
Selecciona marca
         ↓
Envía a /scrape (POST)
         ↓
Backend inicia driver Selenium
         ↓
Llama al scraper correspondiente
         ↓
Extrae datos del producto
         ↓
Calcula precios y ganancias
         ↓
Crea DataFrame con pandas
         ↓
Guarda como Excel con openpyxl
         ↓
Devuelve nombre de archivo
         ↓
Frontend descarga Excel
         ↓
Usuario recibe catálogo
```

---

## 🐛 Debugging

### Ver logs en consola
Cuando ejecutas `run.py`, ves todos los logs en tiempo real

### Errores comunes

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError` | Activar venv: `.\venv\Scripts\activate` |
| `Port 5000 in use` | Cambiar puerto en `app.py` |
| `Chrome not found` | `pip install --upgrade webdriver-manager` |
| `Git not found` | Instalar Git desde git-scm.com |

---

## 📈 Próximas Mejoras

- [ ] Agregar Amazon y eBay al mismo nivel
- [ ] Cachés de datos
- [ ] Base de datos SQLite
- [ ] Histórico de catálogos generados
- [ ] Dashboard con estadísticas
- [ ] Sincronización en tiempo real
- [ ] Autenticación de usuario
- [ ] API REST completa

---

## 📄 Notas Importantes

✅ **Internet requerido** - Para scraping en vivo
✅ **Chrome instalado** - WebDriver necesita Chrome
✅ **Permisos de escritura** - Para generar Excel en Descargas
✅ **Tiempo** - Primero scrape es más lento (descarga ChromeDriver)

---

## 🤝 Soporte Técnico

Para reportar bugs o agregar features:
1. GitHub Issues: https://github.com/JoshuaMzV/Scrapping-Web
2. Contacto directo

---

**Última actualización**: 19/11/2025
**Versión**: 1.0.0
**Estado**: Producción ✅
