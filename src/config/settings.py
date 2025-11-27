"""
Configuración centralizada de la aplicación
"""
import os
from datetime import datetime

# VERSION HANDLING
def get_version():
    """Return the application version.
    Priority:
    1. Environment variable APP_VERSION (set by CI).
    2. version.txt at project root (two levels up from this file).
    3. Fallback to '3.0.0'.
    """
    # 1. Check environment variable
    env_version = os.getenv('APP_VERSION')
    if env_version:
        return env_version.strip()
    # 2. Look for version.txt in project root
    try:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        version_file = os.path.join(base_path, 'version.txt')
        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    # 3. Fallback
    return '3.0.0'

VERSION = get_version()

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


# 1. LISTAS MAESTRAS DE MARCAS (Nombres Canónicos)
RAW_MODA_BRANDS = [
    'Nike', 'Jordan', 'Adidas', 'Yeezy', 'Puma', 'New Balance', 'Under Armour',
    'Gucci', 'Prada', 'Zara', 'H&M', 'Shein', 'Forever 21', 'Bershka', 'Pull&Bear',
    'Stradivarius', 'Massimo Dutti', 'Mango', 'ASOS', 'Boohoo', 'Fashion Nova',
    'Gymshark', 'Lululemon', 'Alo Yoga', 'Fabletics', 'Victoria\'s Secret',
    'Calvin Klein', 'Tommy Hilfiger', 'Ralph Lauren', 'Lacoste', 'Hugo Boss',
    'Versace', 'Dolce & Gabbana', 'Burberry', 'Fendi', 'Balenciaga',
    'Saint Laurent', 'Alexander McQueen', 'Off-White', 'Supreme',
    'BAPE', 'Kith', 'Palace', 'Stussy', 'Obey', 'Vans', 'Converse', 'Reebok',
    'Asics', 'Saucony', 'Brooks', 'Hoka', 'On Running', 'Salomon', 'Timberland',
    'Dr. Martens', 'UGG', 'Crocs', 'Birkenstock', 'Clarks', 'Steve Madden',
    'Aldo', 'Nine West', 'Michael Kors', 'Coach', 'Kate Spade', 'Tory Burch',
    'Marc Jacobs'
]

RAW_COSMETICS_BRANDS = [
    'Ulta', 'MAC', 'MAC Cosmetics', 'NARS', 'Urban Decay', 'Fenty Beauty', 'Huda Beauty',
    'Anastasia Beverly Hills', 'Too Faced', 'Benefit', 'Tarte', 'Smashbox',
    'Clinique', 'Estée Lauder', 'Lancôme', 'Dior', 'Dior Makeup', 'Chanel', 'Chanel Makeup',
    'YSL Beauty', 'Yves Saint Laurent', 'Giorgio Armani Beauty', 'Tom Ford Beauty', 'Charlotte Tilbury',
    'Pat McGrath', 'Natasha Denona', 'Kylie Cosmetics', 'Rare Beauty', 'Glossier',
    'ColourPop', 'Morphe', 'NYX', 'Maybelline', 'L\'Oréal', 'Revlon', 'CoverGirl',
    'e.l.f.', 'Wet n Wild', 'Milani', 'Physicians Formula', 'Neutrogena', 'CeraVe',
    'La Roche-Posay', 'Vichy', 'Avène', 'Bioderma', 'The Ordinary',
    'Paula\'s Choice', 'Drunk Elephant', 'Tatcha', 'Laneige', 'Glow Recipe',
    'Sunday Riley', 'Farmacy', 'Fresh', 'Kiehl\'s', 'Origins', 'Shiseido',
    'SK-II', 'La Mer', 'Sisley', 'Clarins', 'L\'Occitane', 'Bath & Body Works',
    'Victoria\'s Secret Beauty', 'Lush', 'The Body Shop', 'Aesop', 'Le Labo',
    'Diptyque', 'Byredo', 'Jo Malone', 'Creed', 'Maison Francis Kurkdjian',
    'Parfums de Marly', 'Roja Parfums', 'Xerjoff', 'Amouage', 'Montale',
    'Mancera', 'Nishane', 'BDK Parfums', 'Goldfield & Banks', 'Imaginary Authors',
    'Zoologist', 'Dieux', 'Sol de Janeiro', 'Olehenriksen', 'Touchland', 'Saie',
    'Elemis', 'Josie Maran', 'Supergoop!', 'Abeille Royale', 'Carolina Herrera',
    'Givenchy', 'Guerlain', 'Bare Minerals', 'Valentino'
]

RAW_TECH_BRANDS = [
    'Apple', 'Samsung', 'Sony', 'Dell', 'HP'
]

# 2. ALIAS MANUALES (Variaciones -> Nombre Canónico)
BRAND_ALIASES = {
    'fenty belleza': 'Fenty Beauty',
    'cosméticos mac': 'MAC Cosmetics',
    'cosméticos nars': 'NARS',
    'minerales desnudos': 'Bare Minerals',
    'cosméticos nyx': 'NYX',
    'olehenrik sen': 'Olehenriksen',
    'ysl': 'Yves Saint Laurent',
    'mac': 'MAC Cosmetics',
}

# 3. GENERACIÓN AUTOMÁTICA
CATEGORIA_MODA = set(RAW_MODA_BRANDS)
CATEGORIA_COSMETICOS = set(RAW_COSMETICS_BRANDS)

MARCAS_KEYWORDS = {}

def _add_brands(brand_list):
    for brand in brand_list:
        MARCAS_KEYWORDS[brand.lower()] = brand

_add_brands(RAW_MODA_BRANDS)
_add_brands(RAW_COSMETICS_BRANDS)
_add_brands(RAW_TECH_BRANDS)

# Sobrescribir con alias
MARCAS_KEYWORDS.update(BRAND_ALIASES)

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
