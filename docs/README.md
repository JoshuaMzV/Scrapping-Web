# 📦 Generador de Catálogos - Scraping Web

Aplicación automatizada para generar catálogos de productos desde múltiples tiendas en línea (Nike, Sephora, Amazon, eBay).

## 🎯 Características

- ✅ **Interfaz Moderna**: UI intuitiva y responsiva
- ✅ **Multi-marca**: Soporte para Nike, Sephora, Amazon, eBay
- ✅ **Cálculos Automáticos**: Precios, márgenes y ganancias
- ✅ **Excel Automático**: Genera catálogos en Excel
- ✅ **Actualizaciones desde GitHub**: Sistema de auto-actualización
- ✅ **Escalable**: Fácil de agregar nuevas marcas

## 🚀 Uso Rápido

### Opción 1: Ejecutable (.exe) - Recomendado

1. Descarga `CatalogoGenerator.exe`
2. Haz doble clic para abrir
3. Pega los links de productos
4. ¡Genera tu catálogo!

### Opción 2: Desde Python

#### Instalación

```bash
# Clonar repositorio
git clone https://github.com/JoshuaMzV/Scrapping-Web.git
cd Scrapping-Web

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

#### Ejecutar

```bash
python run.py
```

Se abrirá automáticamente en `http://127.0.0.1:5000`

## 📝 Instrucciones de Uso

1. **Selecciona la marca** de la que quieres extraer datos
2. **Pega los links** (uno por línea) que guardaste
3. **Haz clic en "Generar Catálogo"**
4. **Descarga automática** del Excel con:
   - Nombre del producto
   - Tallas disponibles
   - Precio original (USD)
   - Costo final (USD y GTQ)
   - Precio sugerido de venta
   - Ganancia por unidad
   - Margen de ganancia (%)

## 🔄 Actualización desde GitHub

En la sección **⚙️ Configuración**:

1. Ingresa la URL de tu repositorio: `https://github.com/usuario/repo`
2. Haz clic en **"Actualizar Ahora"**
3. La aplicación descargará los últimos cambios
4. Reinicia la aplicación

## 📁 Estructura del Proyecto

```
scraping_project/
├── app.py                 # Backend Flask
├── run.py                 # Script para ejecutar
├── build_exe.py           # Script para empaquetar a .exe
├── requirements.txt       # Dependencias
├── templates/
│   └── index.html        # Interfaz web
├── static/
│   ├── css/
│   │   └── style.css     # Estilos
│   └── js/
│       └── script.js     # Lógica frontend
└── scrapers/
    ├── nike.py           # Scraper de Nike
    └── sephora.py        # Scraper de Sephora
```

## 🔧 Agregar Nueva Marca

### 1. Crear el scraper

Crea `scrapers/nueva_marca.py`:

```python
def scrape_nueva_marca(driver, wait, url):
    """Función para extraer datos"""
    try:
        driver.get(url)
        # Tu lógica de scraping aquí
        return {"nombre": nombre, "precio": precio, "imagen": imagen, "tallas": tallas}
    except Exception as e:
        return {"nombre": "Error", "precio": "Error", "imagen": "Error", "tallas": "Error"}

def calcular_precios(precio_usd):
    """Calcula precios y ganancias"""
    # Lógica de cálculo
    return {...}
```

### 2. Actualizar `app.py`

En la función `scrape()`, agrega:

```python
elif 'nueva_marca' in marca.lower():
    datos_extraidos = scrape_nueva_marca(driver, wait, url)
    calcular = nueva_marca_calcular
```

### 3. Actualizar `index.html`

En el selector de marca, agrega:

```html
<option value="nueva_marca">🔍 Nueva Marca</option>
```

## 🛠️ Crear Ejecutable (.exe)

```bash
python build_exe.py
```

El ejecutable se creará en la carpeta `dist/`

## 📦 Dependencias

- **Flask**: Servidor web
- **Selenium**: Web scraping
- **Pandas**: Procesamiento de datos
- **openpyxl**: Generación de Excel
- **webdriver-manager**: Gestión automática de ChromeDriver

## ⚙️ Configuración

### Precios (en `scrapers/`)

Modifica estas variables según tu negocio:

```python
PORCENTAJE_COSTO_CAJA = 8.0          # % del costo
PORCENTAJE_COSTO_ENVIO = 5.0         # % envío
PORCENTAJE_SEGURO = 3.0              # % seguro
TASA_CAMBIO_GTQ = 7.8                # USD a GTQ
MULTIPLICADOR_PRECIO_MERCADO = 1.40  # Multiplicador mercado local
FACTOR_DESCUENTO_VENTA = 0.90        # Descuento en venta
```

## 📝 Notas

- Requiere **conexión a internet** para scraping
- Chrome debe estar disponible en el sistema
- Los Excel se descargan a la carpeta **Descargas** por defecto

## 🐛 Solución de Problemas

### "Chrome driver no encontrado"
```bash
pip install --upgrade webdriver-manager
```

### "No se puede conectar al servidor"
Asegúrate de que el puerto 5000 está disponible

### "Error al descargar archivo"
Verifica permisos en la carpeta Descargas

## 📄 Licencia

Proyecto para uso interno

## 👤 Autor

Joshua M. - Desarrollador

## 🤝 Soporte

Para reportar bugs o sugerencias, crea un issue en GitHub.

---

**Última actualización**: 19/11/2025
