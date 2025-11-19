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

# URL de eBay que tiene múltiples opciones (color, talla)
url = 'https://www.ebay.com/itm/357896320478'

print("=" * 80)
print("TEST: eBay con opciones multiples (Color + Talla)")
print("=" * 80)
print(f"URL: {url}\n")

result = scrape_nike(driver, wait, url)

if result:
    print("\nRESULTADO:")
    print(f"  Nombre: {result['nombre'][:70]}")
    print(f"  Precio: {result['precio']}")
    print(f"  Tallas: {result['tallas']}")
    print(f"  Sitio: {result['sitio']}")
else:
    print("\nError al extraer datos")

driver.quit()
print("\n[OK] Test completado")

