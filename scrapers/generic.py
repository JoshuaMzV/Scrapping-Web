"""
Scraper Genérico para sitios de cosméticos y moda.
Intenta extraer información usando estándares web:
1. OpenGraph Tags (og:title, og:image, etc.)
2. Schema.org JSON-LD (Product, Offer)
3. Selectores comunes (h1, .price, etc.)
"""

from selenium.webdriver.common.by import By
import json
import re

def scrape_generic(driver, wait, url):
    """
    Intenta extraer datos de cualquier sitio e-commerce usando metadatos estándar.
    """
    try:
        driver.get(url)
        # Dar tiempo a que cargue JS (SPA frameworks)
        import time
        time.sleep(3)
        
        # 1. Extracción por OpenGraph (Meta Tags)
        og_data = {}
        metas = driver.find_elements(By.CSS_SELECTOR, 'meta[property^="og:"]')
        for meta in metas:
            prop = meta.get_attribute('property')
            content = meta.get_attribute('content')
            if prop and content:
                og_data[prop] = content
        
        nombre = og_data.get('og:title')
        imagen = og_data.get('og:image')
        sitio = og_data.get('og:site_name', 'Sitio Desconocido')
        
        # 2. Extracción por JSON-LD (Schema.org)
        json_ld_data = None
        scripts = driver.find_elements(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
        for script in scripts:
            try:
                data = json.loads(script.get_attribute('innerHTML'))
                # Puede ser una lista o un dict
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Product':
                            json_ld_data = item
                            break
                elif isinstance(data, dict):
                    if data.get('@type') == 'Product':
                        json_ld_data = data
                    elif '@graph' in data: # Estructura graph
                        for item in data['@graph']:
                            if item.get('@type') == 'Product':
                                json_ld_data = item
                                break
                if json_ld_data:
                    break
            except:
                continue
        
        # Refinar datos con JSON-LD si existe
        if json_ld_data:
            if not nombre:
                nombre = json_ld_data.get('name')
            if not imagen:
                img = json_ld_data.get('image')
                if isinstance(img, list):
                    imagen = img[0]
                elif isinstance(img, dict):
                    imagen = img.get('url')
                else:
                    imagen = img
            if not sitio or sitio == 'Sitio Desconocido':
                brand = json_ld_data.get('brand')
                if isinstance(brand, dict):
                    sitio = brand.get('name')
                elif isinstance(brand, str):
                    sitio = brand
        
        # 3. Fallbacks para Nombre
        if not nombre:
            try:
                nombre = driver.find_element(By.TAG_NAME, 'h1').text.strip()
            except:
                nombre = driver.title
        
        # 4. Extracción de Precio (Lo más difícil)
        precio_str = "0"
        
        # Intento A: JSON-LD Offers
        if json_ld_data and 'offers' in json_ld_data:
            offers = json_ld_data['offers']
            if isinstance(offers, list):
                offers = offers[0] # Tomar la primera oferta
            if isinstance(offers, dict):
                price = offers.get('price')
                if price:
                    precio_str = str(price)
        
        # Intento B: OpenGraph Price
        if precio_str == "0":
            precio_str = og_data.get('product:price:amount', "0")
            
        # Intento C: Selectores comunes de precio
        if precio_str == "0":
            common_price_selectors = [
                '[data-test="product-price"]', # Target
                '.price', '.product-price', '.pdp-price', 
                '.Price', '.current-price', 
                'span[itemprop="price"]',
                'div[class*="price"]', 'span[class*="price"]'
            ]
            for selector in common_price_selectors:
                try:
                    elems = driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elems:
                        txt = el.text.strip()
                        # Buscar patrón de precio ($12.34)
                        if re.search(r'[\$€£]?\s?\d+[.,]\d+', txt):
                            precio_str = txt
                            break
                    if precio_str != "0":
                        break
                except:
                    continue

        # Limpieza final de nombre (quitar " | Ulta Beauty", etc.)
        if nombre:
            separators = [' | ', ' - ', ' : ']
            for sep in separators:
                if sep in nombre:
                    parts = nombre.split(sep)
                    # Quedarse con la parte más larga que suele ser el nombre real, 
                    # o la primera si es "Nombre | Marca"
                    if len(parts[0]) > 10: 
                        nombre = parts[0]
                    else:
                        nombre = sorted(parts, key=len, reverse=True)[0]

        # Determinar Marca si no está
        marca = sitio
        
        return {
            "nombre": nombre or "Desconocido", 
            "precio": precio_str, 
            "imagen": imagen or "No encontrada", 
            "tallas": "N/A", 
            "sitio": sitio or "Generico",
            "marca": marca
        }

    except Exception as e:
        print(f"    ❌ Error en Scraper Genérico ({url}): {str(e)[:100]}")
        return None
