"""
Configuración centralizada de la aplicación
"""
import os
from datetime import datetime

# CONFIGURACIÓN DE DIRECTORIOS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# CARPETA DE DATOS EXTERNA (para .exe compilados)
# Si se ejecuta desde PyInstaller, usa carpeta en AppData
if hasattr(os.sys, 'frozen') and hasattr(os.sys, '_MEIPASS'):
    # En .exe compilado
    DATA_DIR = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'CatalogoGenerator', 'data')
else:
    # En desarrollo
    DATA_DIR = BASE_DIR

os.makedirs(DATA_DIR, exist_ok=True)

# CONFIGURACIÓN DE FLASK
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000
FLASK_DEBUG = False
UPLOAD_FOLDER = os.path.join(os.path.expanduser('~'), 'Downloads')
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

# CONFIGURACIÓN DE SELENIUM
SELENIUM_TIMEOUT = 20
SELENIUM_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# CONFIGURACIÓN DE SCRAPING - PRECIOS
PORCENTAJE_COSTO_CAJA = 8.0
PORCENTAJE_COSTO_ENVIO = 5.0
PORCENTAJE_SEGURO = 3.0
TASA_CAMBIO_GTQ = 7.8
MULTIPLICADOR_PRECIO_MERCADO = 1.40
FACTOR_DESCUENTO_VENTA = 0.90

# CONFIGURACIÓN DE GITHUB
GITHUB_REPO_URL = 'https://github.com/JoshuaMzV/Scrapping-Web'
GITHUB_REPO_OWNER = 'JoshuaMzV'
GITHUB_REPO_NAME = 'Scrapping-Web'
VERSION = '1.0.6'
LAST_UPDATE = datetime.now().strftime('%d/%m/%Y')

# MARCAS SOPORTADAS
MARCAS_SOPORTADAS = {
    'nike': 'Nike',
    'sephora': 'Sephora'
}

# PALABRAS CLAVE PARA DETECCIÓN DE PRODUCTOS CON TALLAS
PALABRAS_CLAVE_CON_TALLAS = [
    'air force', 'jordan', 'shoe', 'zapato', 'tenis', 'pantalon', 
    'pantalón', 'sudadera', 'chaqueta', 'jacket', 'pants', 'shorts'
]

# PALABRAS CLAVE PARA PRODUCTOS SIN TALLAS
PALABRAS_CLAVE_SIN_TALLAS = [
    'serum', 'cosmetic', 'maquillaje', 'phone', 'laptop', 'electrónica',
    'electronica', 'skincare', 'cream', 'lotion', 'foundation', 'lipstick'
]

# LOGGING
LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
LOG_LEVEL = 'INFO'
