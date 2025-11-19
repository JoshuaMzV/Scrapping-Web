"""
Scraper para productos SEPHORA
Detecta automáticamente el sitio (Sephora.com, Amazon, eBay, etc.) y adapta el scraping
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# --- CONFIGURACIÓN DE COSTOS ---
PORCENTAJE_COSTO_CAJA = 8.0
PORCENTAJE_COSTO_ENVIO = 5.0
PORCENTAJE_SEGURO = 3.0

# --- CONFIGURACIÓN DE PRECIOS ---
TASA_CAMBIO_GTQ = 7.8
MULTIPLICADOR_PRECIO_MERCADO = 1.40
FACTOR_DESCUENTO_VENTA = 0.90


def scrape_sephora_desde_sephora_com(driver, wait, url):
    """Scraper específico para Sephora.com"""
    try:
        driver.get(url)
        time.sleep(1)
        
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-at="product_name"]')))
        nombre = driver.find_element(By.CSS_SELECTOR, '[data-at="product_name"]').text
        
        precio_str = "0"
        try:
            precio_str = driver.find_element(By.XPATH, '//b[starts-with(text(), "$")]').text
        except:
            pass
        
        imagen = "No encontrada"
        try:
            imagen = driver.find_element(By.CSS_SELECTOR, 'img[src*="/sku/"]').get_attribute('src')
        except:
            pass
        
        return {"nombre": nombre, "precio": precio_str, "imagen": imagen, "tallas": "N/A", "sitio": "Sephora.com"}
    except Exception as e:
        print(f"    ❌ Error en Sephora.com: {str(e)[:50]}")
        return None


def scrape_sephora_desde_amazon(driver, wait, url):
    """Scraper para productos Sephora en Amazon"""
    try:
        driver.get(url)
        time.sleep(2)

        wait.until(EC.visibility_of_element_located((By.ID, "productTitle")))
        nombre = driver.find_element(By.ID, "productTitle").text
        
        precio_str = "0"
        try:
            precio_str = driver.find_element(By.CSS_SELECTOR, 'span.aok-offscreen').text
        except:
            pass

        imagen = "No encontrada"
        try:
            imagen = driver.find_element(By.ID, "landingImage").get_attribute('src')
        except:
            pass
        
        return {"nombre": nombre, "precio": precio_str, "imagen": imagen, "tallas": "N/A", "sitio": "Amazon"}
    except Exception as e:
        print(f"    ❌ Error en Amazon: {str(e)[:50]}")
        return None


def scrape_sephora_desde_ebay(driver, wait, url):
    """Scraper para productos Sephora en eBay"""
    try:
        driver.get(url)
        time.sleep(1)

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.x-item-title__mainTitle span')))
        nombre = driver.find_element(By.CSS_SELECTOR, 'h1.x-item-title__mainTitle span').text
        
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.x-price-primary span.ux-textspans')))
        precio_str = driver.find_element(By.CSS_SELECTOR, 'div.x-price-primary span.ux-textspans').text
        
        imagen = "No encontrada"
        try:
            imagen = driver.find_element(By.CSS_SELECTOR, 'img[src*="ebayimg.com"]').get_attribute('src')
        except:
            pass
        
        return {"nombre": nombre, "precio": precio_str, "imagen": imagen, "tallas": "N/A", "sitio": "eBay"}
    except Exception as e:
        print(f"    ❌ Error en eBay: {str(e)[:50]}")
        return None


def scrape_sephora(driver, wait, url):
    """
    Scraper inteligente para Sephora que detecta el sitio automáticamente
    y usa el scraper específico
    """
    print(f"    🔍 Detectando sitio...", end="")
    
    if "sephora.com" in url.lower():
        print(" Sephora.com")
        return scrape_sephora_desde_sephora_com(driver, wait, url)
    elif "amazon" in url.lower():
        print(" Amazon")
        return scrape_sephora_desde_amazon(driver, wait, url)
    elif "ebay" in url.lower():
        print(" eBay")
        return scrape_sephora_desde_ebay(driver, wait, url)
    else:
        print(" Sitio desconocido")
        return None


def calcular_precios(precio_usd):
    """Calcula los precios y ganancias"""
    try:
        precio_usd = float(precio_usd)
    except (ValueError, TypeError):
        precio_usd = 0.0

    costo_caja = precio_usd * (PORCENTAJE_COSTO_CAJA / 100)
    costo_envio = precio_usd * (PORCENTAJE_COSTO_ENVIO / 100)
    subtotal = precio_usd + costo_caja + costo_envio
    costo_seguro = subtotal * (PORCENTAJE_SEGURO / 100)
    costo_final_usd = subtotal + costo_seguro
    
    precio_mercado_gtq = (precio_usd * MULTIPLICADOR_PRECIO_MERCADO) * TASA_CAMBIO_GTQ 
    precio_venta_gtq = precio_mercado_gtq * FACTOR_DESCUENTO_VENTA
    
    costo_final_gtq = costo_final_usd * TASA_CAMBIO_GTQ
    ganancia_gtq = precio_venta_gtq - costo_final_gtq
    margen_ganancia = (ganancia_gtq / precio_venta_gtq) * 100 if precio_venta_gtq > 0 else 0

    return {
        "Precio Original (USD)": round(precio_usd, 2),
        "Costo Final por Unidad (USD)": round(costo_final_usd, 2),
        "Costo Final por Unidad (GTQ)": round(costo_final_gtq, 2),
        "Precio Sugerido Venta (GTQ)": round(precio_venta_gtq, 2),
        "Ganancia por Unidad (GTQ)": round(ganancia_gtq, 2),
        "Margen de Ganancia (%)": round(margen_ganancia, 2),
    }


def limpiar_precio(precio_str):
    """Limpia el string de precio"""
    precio_limpio = re.sub(r'[^\d.]', '', precio_str)
    try:
        return float(precio_limpio)
    except:
        return 0.0
