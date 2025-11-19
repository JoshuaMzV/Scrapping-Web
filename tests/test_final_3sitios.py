from scrapers.nike import scrape_nike, calcular_precios as nike_calcular, limpiar_precio
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import os
from datetime import datetime
import time

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

urls = [
    'https://www.nike.com/es/t/air-force-1-07-zapatillas-E5NnNyBr/CW2288-111',
    'https://www.ebay.com/itm/357896320478',
    'https://www.amazon.com/-/es/Nike-Air-Force-107-baloncesto/dp/B08QBJFKF3/ref=sr_1_1?sr=8-1&psc=1',
]

print("=" * 80)
print("PRUEBA FINAL: Scraping Nike (3 sitios)")
print("=" * 80)

datos_encontrados = []

for idx, url in enumerate(urls, 1):
    print(f"\n[{idx}/3] {url[:60]}...")
    
    result = scrape_nike(driver, wait, url)
    
    if result and result.get('nombre') != 'Error':
        precio_usd = limpiar_precio(result['precio'])
        precios = nike_calcular(precio_usd)
        
        row = {
            'Nombre del Producto': result['nombre'],
            'Sitio': result['sitio'],
            'Tallas Disponibles': result['tallas'],
            'URL Imagen': result.get('imagen', ''),
            'URL Producto': url,
            **precios
        }
        datos_encontrados.append(row)
        print(f"    OK: {result['nombre'][:50]}")

driver.quit()

if datos_encontrados:
    df = pd.DataFrame(datos_encontrados)
    
    # Guardar en Downloads
    downloads = os.path.expanduser("~\\Downloads")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"catalogo_nike_FINAL_{timestamp}.xlsx"
    filepath = os.path.join(downloads, filename)
    
    df.to_excel(filepath, index=False)
    print(f"\n[OK] Archivo generado: {filename}")
    print(f"\nResumen:")
    print(f"  Productos: {len(df)}")
    for idx, row in df.iterrows():
        print(f"  {idx + 1}. {row['Sitio']}: {row['Tallas Disponibles'][:40]}")
else:
    print("\n[ERROR] No se capturaron datos")
