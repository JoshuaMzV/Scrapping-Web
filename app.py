from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import re
import time
import gc
from datetime import datetime
import subprocess
import shutil
import json
from io import BytesIO
import base64

# Importar scrapers
from scrapers.nike import scrape_nike, calcular_precios as nike_calcular, limpiar_precio as nike_limpiar
from scrapers.sephora import scrape_sephora, calcular_precios as sephora_calcular, limpiar_precio as sephora_limpiar

# Importar configuración
from src.config.settings import GITHUB_REPO_URL, GITHUB_REPO_OWNER, GITHUB_REPO_NAME, VERSION

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.expanduser('~'), 'Downloads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Configuración global
DRIVER = None
WAIT = None

def inicializar_driver():
    """Inicializa el driver de Selenium"""
    global DRIVER, WAIT
    if DRIVER is None:
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        DRIVER = webdriver.Chrome(service=service, options=options)
        WAIT = WebDriverWait(DRIVER, 20)
    return DRIVER, WAIT

def cerrar_driver():
    """Cierra el driver de Selenium"""
    global DRIVER
    if DRIVER:
        try:
            DRIVER.quit()
            DRIVER = None
        except:
            pass

def limpiar_precio(precio_str):
    """Limpia el string de precio y retorna float"""
    # Reemplazar coma por punto (para locales que usan coma como decimal)
    precio_limpio = precio_str.replace(',', '.')
    # Remover todo excepto dígitos y puntos
    precio_limpio = re.sub(r'[^\d.]', '', precio_limpio)
    try:
        return float(precio_limpio)
    except:
        return 0.0

def es_producto_con_tallas(nombre_producto):
    """Determina si el producto debe tener columna de tallas"""
    nombre_lower = nombre_producto.lower()
    
    # Palabras clave que indican productos SIN tallas (electrónica, maquillaje) - PRIMERA PRIORIDAD
    palabras_sin_tallas = [
        'pc', 'laptop', 'computadora', 'computer', 'teléfono', 'phone', 'móvil', 'celular',
        'tablet', 'ipad', 'monitor', 'pantalla', 'tv', 'television', 'mouse', 'teclado',
        'maquillaje', 'makeup', 'cosmético', 'lipstick', 'labial', 'rimmel', 'sombra',
        'perfume', 'fragancia', 'cologne', 'crema', 'loción', 'jabón', 'shampoo',
        'auricular', 'headphone', 'cable', 'cargador', 'charger', 'bateria', 'battery',
        'funda', 'case', 'protector', 'glass', 'mica', 'pantalla protectora',
        'serum', 'suero', 'aceite', 'oil', 'facial', 'tratamiento', 'treatment',
        'limpiador', 'cleanser', 'tónico', 'toner', 'máscara', 'mask', 'hidratante',
        'gel', 'espuma', 'foam', 'exfoliante', 'scrub', 'esencia', 'essence'
    ]
    
    # Palabras clave que indican productos CON tallas (ropa, zapatos)
    palabras_con_tallas = [
        'zapato', 'shoe', 'calzado', 'tenis', 'sneaker', 'boot', 'bota',
        'camisa', 'shirt', 'pantalon', 'pants', 'jean', 'jeans',
        'remera', 'blusa', 'chaqueta', 'jacket', 'abrigo', 'coat',
        'vestido', 'dress', 'falda', 'skirt', 'sudadera', 'hoodie',
        'manga', 'sleeve', 'talla', 'size', 'xs', 's', 'm', 'l', 'xl', 'xxl',
        'polo', 't-shirt', 'camiseta', 'short', 'medias', 'socks',
        'air force', 'jordan', 'adidas', 'puma', 'converse',  # Marcas de zapatos
        'zapatilla', 'deportiva', 'running', 'basketball'
    ]
    
    # Si contiene palabras sin tallas, retornar False
    for palabra in palabras_sin_tallas:
        if palabra in nombre_lower:
            return False
    
    # Si contiene palabras con tallas, retornar True
    for palabra in palabras_con_tallas:
        if palabra in nombre_lower:
            return True
    
    # Por defecto, sin tallas (la mayoría de productos modernos no las necesitan)
    return False

# RUTAS

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    """Endpoint para scraping"""
    try:
        data = request.get_json()
        marca = data.get('marca')
        links = data.get('links', [])

        if not marca or not links:
            return jsonify({'success': False, 'message': 'Marca o links vacíos'}), 400

        print(f"\n🚀 Iniciando scraping de {marca}...")
        print(f"📝 Links a procesar: {len(links)}")

        driver, wait = inicializar_driver()
        datos_encontrados = []

        # Determinar scraper según marca
        if 'nike' in marca.lower():
            scraper_func = scrape_nike
            calcular = nike_calcular
        elif 'sephora' in marca.lower():
            scraper_func = scrape_sephora
            calcular = sephora_calcular
        else:
            return jsonify({'success': False, 'message': f'Marca "{marca}" no soportada'}), 400

        for idx, url in enumerate(links, 1):
            print(f"\n[{idx}/{len(links)}] Procesando: {url}")
            
            try:
                # El scraper detecta automáticamente el sitio (Nike.com, Amazon, eBay, etc.)
                datos_extraidos = scraper_func(driver, wait, url)

                if datos_extraidos and datos_extraidos.get('nombre') != 'Error':
                    # Calcular precios
                    precio_usd = limpiar_precio(datos_extraidos['precio'])
                    precios = calcular(precio_usd)

                    # Compilar datos (incluye sitio donde fue encontrado)
                    row = {
                        'Nombre del Producto': datos_extraidos['nombre'],
                        'Sitio': datos_extraidos.get('sitio', 'Desconocido'),
                        'Tallas Disponibles': datos_extraidos.get('tallas', 'N/A'),
                        'URL Imagen': datos_extraidos.get('imagen', ''),
                        'URL Producto': url,
                        **precios
                    }
                    datos_encontrados.append(row)
                    print(f"✅ {datos_extraidos['nombre']} ({datos_extraidos.get('sitio', 'sitio')})")
                else:
                    print(f"❌ Error extrayendo datos")

            except Exception as e:
                print(f"❌ Error con {url}: {str(e)}")
                continue

        cerrar_driver()

        if not datos_encontrados:
            return jsonify({'success': False, 'message': 'No se extrajeron datos'}), 400

        # Crear Excel
        df = pd.DataFrame(datos_encontrados)
        
        # Remover columna de tallas para productos que no la necesitan
        if 'Tallas Disponibles' in df.columns:
            # Revisar cada producto y determinar si debe mantener tallas
            productos_sin_tallas = []
            for idx, row in df.iterrows():
                nombre = row.get('Nombre del Producto', '')
                tiene_tallas = es_producto_con_tallas(nombre)
                print(f"   → '{nombre[:50]}...' → Tallas: {tiene_tallas}")
                if not tiene_tallas:
                    productos_sin_tallas.append(idx)
            
            # Si TODOS los productos no necesitan tallas, remover columna
            if len(productos_sin_tallas) == len(df):
                df = df.drop(columns=['Tallas Disponibles'])
                print(f"📊 Columna 'Tallas Disponibles' removida (todos los productos: electrónica/maquillaje)")
            elif productos_sin_tallas:
                # Si solo algunos no necesitan tallas, poner "N/A" para esos
                for idx in productos_sin_tallas:
                    df.at[idx, 'Tallas Disponibles'] = 'N/A'
                print(f"📊 {len(productos_sin_tallas)} productos marcados como 'N/A' (sin tallas relevantes)")
        
        filename = f"catalogo_{marca}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Generar Excel en memoria (sin guardar en disco)
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        buffer.seek(0)
        excel_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        print(f"\n✅ Excel generado en memoria: {filename}")

        return jsonify({
            'success': True,
            'message': f'Catálogo generado con {len(datos_encontrados)} productos',
            'filename': filename,
            'excel_data': excel_base64
        }), 200

    except Exception as e:
        print(f"❌ Error en scrape: {str(e)}")
        cerrar_driver()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/update', methods=['POST'])
def update():
    """Actualiza desde GitHub - URL hardcodeada"""
    try:
        print(f"\n🔄 Descargando actualización desde: {GITHUB_REPO_URL}")

        # Usar URL hardcodeada
        usuario = GITHUB_REPO_OWNER
        repo = GITHUB_REPO_NAME
        project_root = os.path.dirname(__file__)
        
        # Crear carpeta temporal con timestamp
        from datetime import datetime as dt_now
        temp_timestamp = dt_now.now().strftime('%Y%m%d_%H%M%S')
        temp_dir = os.path.join(project_root, f'temp_update_{temp_timestamp}')
        
        # Limpiar directorio temporal si existe (con reintentos)
        if os.path.exists(temp_dir):
            for attempt in range(3):
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    time.sleep(0.5)
                    if not os.path.exists(temp_dir):
                        break
                except:
                    pass
        
        os.makedirs(temp_dir, exist_ok=True)

        # Clonar repositorio - usar shallow clone para más velocidad
        clone_url = f"https://github.com/{usuario}/{repo}.git"
        resultado = subprocess.run(['git', 'clone', '--depth', '1', clone_url, temp_dir], 
                                 capture_output=True, text=True, timeout=60)

        if resultado.returncode != 0:
            print(f"❌ Error clonando: {resultado.stderr}")
            return jsonify({'success': False, 'message': 'Error clonando repositorio'}), 400

        # Copiar archivos importantes
        archivos_copiar = [
            'scrapers/',
            'src/',
            'templates/index.html',
            'static/css/style.css',
            'static/js/script.js',
            'requirements.txt',
            'docs/'
        ]
        
        for archivo in archivos_copiar:
            src = os.path.join(temp_dir, archivo)
            dst = os.path.join(project_root, archivo)
            
            if os.path.exists(src):
                try:
                    if os.path.isdir(src):
                        print(f"  📁 Actualizando carpeta: {archivo}")
                        if os.path.exists(dst):
                            shutil.rmtree(dst, ignore_errors=True)
                        shutil.copytree(src, dst, ignore=shutil.ignore_patterns('.git*'))
                    else:
                        print(f"  📄 Actualizando archivo: {archivo}")
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                        shutil.copy2(src, dst)
                except Exception as e:
                    print(f"  ⚠️  Error copiando {archivo}: {e}")

        # Limpiar temp_dir más agresivamente
        import gc
        gc.collect()
        time.sleep(1)
        
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass

        print(f"\n✅ Actualización completada desde: {GITHUB_REPO_URL}")
        return jsonify({
            'success': True, 
            'message': 'Actualización completada. Por favor reinicia la aplicación.',
            'version': VERSION
        }), 200

    except subprocess.TimeoutExpired:
        print("❌ Timeout en descarga de GitHub")
        return jsonify({'success': False, 'message': 'Timeout en descarga (conexión lenta)'}), 400
    except Exception as e:
        print(f"❌ Error en actualización: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok'}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Ruta no encontrada'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Error del servidor'}), 500

if __name__ == '__main__':
    try:
        # Configuración para .exe
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Cerrando aplicación...")
        cerrar_driver()
    except Exception as e:
        print(f"❌ Error: {e}")
        cerrar_driver()
