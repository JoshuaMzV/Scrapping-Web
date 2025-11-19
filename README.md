# 📦 Catálogo Generator

**Sistema de extracción de datos de productos de múltiples sitios web**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.1-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Descripción

Catálogo Generator es una herramienta profesional que permite:
- ✅ Extraer información de productos de cualquier marca
- ✅ Detectar automáticamente el sitio (Nike.com, Amazon, eBay, Sephora, etc.)
- ✅ Generar catálogos en Excel con datos procesados
- ✅ Calcular precios con márgenes configurables
- ✅ Interfaz web intuitiva y moderna

---

## 🚀 Inicio Rápido

### 1. Requisitos
- Python 3.8+
- Entorno virtual (venv)
- Navegador web moderno

### 2. Instalación

```bash
# Clonar o descargar el proyecto
cd scraping_project

# Activar entorno virtual
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Ejecutar

```bash
# Desde Windows PowerShell
python main.py

# O usando el script .bat
.\iniciar.bat
```

La aplicación se abrirá en: **http://127.0.0.1:5000**

---

## 📂 Estructura del Proyecto

```
scraping_project/
├── src/                          # 🔧 Código fuente
│   ├── config/
│   │   └── settings.py           # Configuración centralizada
│   ├── scrapers/
│   │   └── (referencias)
│   ├── utils/
│   │   └── helpers.py            # Funciones comunes
│   └── web/
│       ├── app.py                # Aplicación Flask
│       ├── templates/
│       └── static/
│
├── docs/                         # 📚 Documentación
│   ├── MAPA_RAPIDO.md            # Referencia rápida
│   ├── GUIA_ESTRUCTURA.md        # Cómo funciona
│   ├── DESARROLLO.md             # Para programadores
│   └── ... más guías
│
├── tests/                        # ✅ Tests y debug
│   ├── test_*.py
│   └── debug_*.py
│
├── scrapers/                     # 🕷️ Extractores
│   ├── nike.py
│   └── sephora.py
│
├── static/                       # 🎨 CSS, JS
├── templates/                    # 🌐 HTML
├── app.py                        # Aplicación principal
├── main.py                       # Punto de entrada
├── requirements.txt              # Dependencias
└── venv/                         # Entorno virtual
```

---

## 🛠️ Cómo Usar

### Generar Catálogo

1. **Abre la aplicación** en `http://127.0.0.1:5000`
2. **Selecciona marca** (Nike, Sephora, etc.)
3. **Pega links** de cualquier sitio web (uno por línea)
4. **Haz clic en "Generar Catálogo"**
5. **Descarga el Excel** cuando se pida
6. **Elige dónde guardar** (USB, Desktop, Downloads, etc.)

### Soporta Múltiples Sitios

| Marca | Sitios Soportados |
|-------|------------------|
| **Nike** | Nike.com, Amazon, eBay |
| **Sephora** | Sephora.com, Amazon, eBay |
| *(Expandible)* | *(Agregar más marcas)* |

---

## ⚙️ Configuración

### Modificar Parámetros

Edita `src/config/settings.py`:

```python
# Porcentajes de cálculo
PORCENTAJE_COSTO_CAJA = 8.0
PORCENTAJE_COSTO_ENVIO = 5.0
TASA_CAMBIO_GTQ = 7.8
MULTIPLICADOR_PRECIO_MERCADO = 1.40

# Timeouts
SELENIUM_TIMEOUT = 20

# Puerto del servidor
FLASK_PORT = 5000
```

---

## 📖 Documentación

### Para Usuarios
- 📄 `docs/MAPA_RAPIDO.md` - Referencia de archivos
- 📄 `docs/GUIA_ESTRUCTURA.md` - Entender el proyecto

### Para Desarrolladores
- 💻 `docs/DESARROLLO.md` - Guía completa de desarrollo
- 🔄 `docs/ESTRUCTURA_NUEVA.md` - Arquitectura del proyecto
- 📊 `docs/DIAGRAMA_VISUAL.md` - Flujos y diagramas

---

## 🧪 Tests

Ejecutar tests:

```bash
# Instalar pytest
pip install pytest

# Ejecutar todos los tests
pytest tests/

# Test específico
pytest tests/test_scrapers.py -v
```

---

## 🔧 Agregar Nueva Marca

1. Crear archivo `scrapers/mi_marca.py`
2. Implementar función `scrape_mi_marca(driver, wait, url)`
3. Registrar en `src/config/settings.py`
4. Actualizar `app.py` con la nueva marca

Ver `docs/DESARROLLO.md` para instrucciones detalladas.

---

## 🐛 Solución de Problemas

### El navegador no abre
```bash
# Abre manualmente:
http://127.0.0.1:5000
```

### Error de dependencias
```bash
# Reinstala las dependencias:
pip install -r requirements.txt --force-reinstall
```

### Chrome/Selenium no encontrado
```bash
# Se descarga automáticamente, pero si falla:
pip install webdriver-manager --upgrade
```

---

## 📝 Cambios Recientes

**v1.0 (19/11/2025)**
- ✅ Extracción de Nike.com, Amazon, eBay
- ✅ Extracción de Sephora.com, Amazon, eBay
- ✅ Generación de Excel sin guardar automático
- ✅ Estructura profesional implementada
- ✅ Documentación completa

---

## 🎓 Requisitos Técnicos

### Python Packages
```
Flask 3.1.2
Pandas 2.3.3
Selenium 4.38.0
openpyxl 3.0+
webdriver-manager
```

### Sistema
- Windows 10+
- Chrome/Chromium instalado
- 500MB disco libre (+ venv)

---

## 📞 Soporte

Para preguntas o problemas:

1. **Revisa la documentación** en `docs/`
2. **Consulta el código** en `src/`
3. **Ejecuta tests** con pytest
4. **Revisa logs** en la consola

---

## 📄 Licencia

MIT License - Libre para usar y modificar

---

## 🙏 Créditos

Desarrollado con ❤️ para automatizar catálogos de productos

---

**Última actualización:** 19 de Noviembre de 2025

**Estado:** ✅ Listo para Producción

Para comenzar: `python main.py`
