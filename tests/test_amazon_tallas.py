from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
url = 'https://www.amazon.com/-/es/Zapatos-Vision-Nature-hombre-Blanco/dp/B0983LWFXT'
driver.get(url)
time.sleep(3)

print("=== EXTRAYENDO TALLAS ===")

try:
    select_el = driver.find_element(By.CSS_SELECTOR, '#native_dropdown_selected_size_name')
    options = select_el.find_elements(By.TAG_NAME, 'option')
    print(f"✓ Encontradas {len(options)} opciones")
    tallas = [o.text for o in options if o.text.strip()]
    print(f"Tallas: {tallas}")
except Exception as e:
    print(f"Error: {e}")

driver.quit()
