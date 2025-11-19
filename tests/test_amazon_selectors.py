from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
url = 'https://www.amazon.com/-/es/Zapatos-Vision-Nature-hombre-Blanco/dp/B0983LWFXT'
driver.get(url)
time.sleep(3)

print("=== PROBANDO SELECTORES ===")

# Buscar inline-twister
try:
    elem = driver.find_element(By.ID, "inline-twister-row-size_name")
    print("✓ ENCONTRADO: inline-twister-row-size_name")
    items = elem.find_elements(By.CSS_SELECTOR, 'li.swatch-list-item-text')
    print(f"  Items: {len(items)}")
    for i in items[:5]:
        print(f"    - {i.text}")
except Exception as e:
    print(f"✗ inline-twister: {type(e).__name__}")

# Buscar buttons con Size
try:
    buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="Size"]')
    print(f"\n✓ ENCONTRADOS {len(buttons)} buttons con aria-label 'Size'")
    for b in buttons[:3]:
        print(f"  - {b.get_attribute('aria-label')}")
except Exception as e:
    print(f"\n✗ buttons Size: {e}")

# Buscar select normal
try:
    select = driver.find_element(By.ID, 'native_dropdown_selected_size_name')
    print(f"\n✓ ENCONTRADO: select native_dropdown_selected_size_name")
except:
    print(f"\n✗ select native_dropdown_selected_size_name NO existe")

# Buscar ul[role="listbox"]
try:
    listbox = driver.find_element(By.CSS_SELECTOR, 'ul[role="listbox"]')
    print(f"\n✓ ENCONTRADO: ul[role='listbox']")
    options = listbox.find_elements(By.CSS_SELECTOR, 'li[role="option"]')
    print(f"  Options: {len(options)}")
except Exception as e:
    print(f"\n✗ ul[role='listbox']: {type(e).__name__}")

# Buscar div con tallas
try:
    tallas = driver.find_elements(By.CSS_SELECTOR, '[data-a-size-base]')
    print(f"\n✓ ENCONTRADOS {len(tallas)} elementos con data-a-size-base")
except:
    pass

driver.quit()
