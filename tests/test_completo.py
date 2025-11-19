#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test completo del scraper Nike con los 3 sitios principales
"""

from scrapers.nike import scrape_nike, limpiar_precio, calcular_precios
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import time

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20)

urls_test = [
    ('Nike.com', 'https://www.nike.com/es/t/air-force-1-07-zapatillas-E5NnNyBr/CW2288-111'),
    ('Amazon', 'https://www.amazon.com/-/es/Nike-Air-Force-107-baloncesto/dp/B08QBJFKF3/ref=sr_1_1?sr=8-1&psc=1'),
    ('eBay', 'https://www.ebay.com/itm/357896320478?_skw=air+force+1&itmmeta=01KAEM63NVXCM6MFQKMNMP8RXW&hash=item53544875de%3Ag%3AWHcAAeSwTNdpFcaz'),
]

print('\n' + '=' * 100)
print('🔍 TEST COMPLETO DEL SCRAPER NIKE (Con correcciones de precio)')
print('=' * 100)

for sitio_nombre, url in urls_test:
    print(f'\n\n📍 Probando: {sitio_nombre}')
    print('-' * 100)
    
    try:
        result = scrape_nike(driver, wait, url)
        
        if result:
            print(f'✅ Nombre: {result["nombre"][:70]}')
            print(f'✅ Sitio Detectado: {result["sitio"]}')
            print(f'✅ Precio (raw): {repr(result["precio"])}')
            
            precio_usd = limpiar_precio(result['precio'])
            print(f'✅ Precio (limpio): ${precio_usd:.2f}')
            
            if precio_usd > 0:
                precios = calcular_precios(precio_usd)
                print(f'✅ Costo Final USD: ${precios["Costo Final por Unidad (USD)"]:.2f}')
                print(f'✅ Precio Venta GTQ: Q{precios["Precio Sugerido Venta (GTQ)"]:.2f}')
            
            tallas_preview = result['tallas'][:60] if len(result['tallas']) > 60 else result['tallas']
            print(f'✅ Tallas: {tallas_preview}...' if len(result['tallas']) > 60 else f'✅ Tallas: {tallas_preview}')
            
        else:
            print(f'❌ No se pudieron extraer datos de {sitio_nombre}')
            
    except Exception as e:
        print(f'❌ Error: {str(e)[:100]}')
    
    time.sleep(1)

driver.quit()

print('\n' + '=' * 100)
print('✅ TEST COMPLETADO')
print('=' * 100)
