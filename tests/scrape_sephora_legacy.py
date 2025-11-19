import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# --- ================================================================= ---
# ---   SECCIÓN DE CONFIGURACIÓN (LA MISMA QUE ANTES)               ---
# --- ================================================================= ---

# --- Costos Variables como Porcentaje del Precio del Producto ---
PORCENTAJE_COSTO_CAJA = 8.0
PORCENTAJE_COSTO_ENVIO = 5.0
PORCENTAJE_SEGURO = 3.0

# --- Estrategia de Precios para el Mercado Local (Guatemala) ---
TASA_CAMBIO_GTQ = 7.8
MULTIPLICADOR_PRECIO_MERCADO = 1.40
FACTOR_DESCUENTO_VENTA = 0.90

# --- ================================================================= ---
# ---                  LÓGICA DEL SCRAPER (CORREGIDA)               ---
# --- ================================================================= ---

# Lista de URLs de productos de Sephora
urls_a_raspar = [
    "https://www.sephora.com/product/brazilian-crush-body-fragrance-mist-P417312?skuId=1930759&icid2=products%20grid:p417312:product",
    # Puedes agregar más URLs de Sephora aquí
]

datos_encontrados = []

# --- CONFIGURACIÓN DEL NAVEGADOR ---
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
wait = WebDriverWait(driver, 20) 

print("Iniciando proceso de scraping para Sephora (versión corregida)...")

# --- BUCLE PRINCIPAL ---
for url in urls_a_raspar:
    print(f"\nProcesando: {url}")
    
    # Inicializamos variables
    nombre_producto = "Error"
    precio_str = "Error"
    imagen_url = "Error"

    try:
        driver.get(url)

        # --- ESPERAR A QUE CARGUE LA PÁGINA ---
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '[data-at="product_name"]')))
        print("  -> Página de Sephora cargada.")

        # --- EXTRAER DATOS (SELECTORES ROBUSTOS) ---
        
        # 1. Extraer el nombre del producto
        nombre_producto = driver.find_element(By.CSS_SELECTOR, '[data-at="product_name"]').text

        # 2. Extraer el precio (usando XPath)
        elemento_precio = driver.find_element(By.XPATH, '//b[starts-with(text(), "$")]')
        precio_str = elemento_precio.text
        
        # 3. Extraer la imagen (SELECTOR CORREGIDO Y MÁS ROBUSTO)
        # Buscamos cualquier imagen cuyo 'src' contenga '/sku/'
        elemento_img = driver.find_element(By.CSS_SELECTOR, 'img[src*="/sku/"]')
        imagen_url = elemento_img.get_attribute('src')

        print(f"  -> Datos extraídos: {nombre_producto} - {precio_str}")

    except Exception as e:
        print(f"  -> ERROR al extraer datos de Sephora: {e}")

    # --- CÁLCULOS FINANCIEROS (LA LÓGICA ES IDÉNTICA) ---
    precio_limpio = re.sub(r'[^\d.]', '', precio_str)
    try:
        precio_usd = float(precio_limpio)
    except (ValueError, TypeError):
        precio_usd = 0.0

    costo_caja_por_producto = precio_usd * (PORCENTAJE_COSTO_CAJA / 100)
    costo_envio_por_producto = precio_usd * (PORCENTAJE_COSTO_ENVIO / 100)
    subtotal_por_producto = precio_usd + costo_caja_por_producto + costo_envio_por_producto
    costo_seguro_por_producto = subtotal_por_producto * (PORCENTAJE_SEGURO / 100)
    costo_final_por_unidad_usd = subtotal_por_producto + costo_seguro_por_producto
    
    precio_mercado_local_estimado_gtq = (precio_usd * MULTIPLICADOR_PRECIO_MERCADO) * TASA_CAMBIO_GTQ 
    precio_sugerido_venta_gtq = precio_mercado_local_estimado_gtq * FACTOR_DESCUENTO_VENTA
    
    costo_final_por_unidad_gtq = costo_final_por_unidad_usd * TASA_CAMBIO_GTQ
    ganancia_por_unidad_gtq = precio_sugerido_venta_gtq - costo_final_por_unidad_gtq
    margen_ganancia_porcentual = (ganancia_por_unidad_gtq / precio_sugerido_venta_gtq) * 100 if precio_sugerido_venta_gtq > 0 else 0

    # Guardamos todos los datos calculados
    datos_encontrados.append({
        "Nombre del Producto": nombre_producto,
        "Precio Original (USD)": round(precio_usd, 2),
        "Costo Final por Unidad (USD)": round(costo_final_por_unidad_usd, 2),
        "Costo Final por Unidad (GTQ)": round(costo_final_por_unidad_gtq, 2),
        "Precio Sugerido Venta (GTQ)": round(precio_sugerido_venta_gtq, 2),
        "Ganancia por Unidad (GTQ)": round(ganancia_por_unidad_gtq, 2),
        "Margen de Ganancia (%)": round(margen_ganancia_porcentual, 2),
        "URL Imagen": imagen_url,
        "URL Producto": url
    })

# --- LIMPIEZA Y GUARDADO ---
driver.quit()
print("\nProceso finalizado. Cerrando navegador.")

df = pd.DataFrame(datos_encontrados)
nombre_archivo_excel = "catalogo_sephora_final.xlsx"
df.to_excel(nombre_archivo_excel, index=False)

print(f"\n¡Éxito! Tu catálogo de Sephora ha sido guardado en '{nombre_archivo_excel}'.")