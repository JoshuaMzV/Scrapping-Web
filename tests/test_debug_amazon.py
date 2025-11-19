"""
Debug script para verificar estructura de tallas en Amazon
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_amazon():
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # URL específica
        url = "https://www.amazon.com/Nike-Force-Tenis-hombre-Blanco/dp/B01HK4Y3KG"
        print(f"URL: {url}")
        driver.get(url)
        time.sleep(3)
        
        # Metodo 1: native_dropdown
        try:
            select_native = driver.find_element(By.CSS_SELECTOR, '#native_dropdown_selected_size_name')
            options = select_native.find_elements(By.TAG_NAME, 'option')
            print(f"METODO 1 - native_dropdown: ENCONTRADO")
            print(f"Opciones: {[o.text for o in options if o.text.strip()][:5]}")
        except Exception as e:
            print(f"METODO 1 - native_dropdown: NO ENCONTRADO")
            print(f"  Error: {str(e)[:80]}")
        
        # Metodo 2: listboxes
        try:
            listboxes = driver.find_elements(By.CSS_SELECTOR, 'ul[role="listbox"]')
            print(f"\nMETODO 2 - listboxes: {len(listboxes)} encontrados")
            for i, lb in enumerate(listboxes[:3]):
                options = lb.find_elements(By.CSS_SELECTOR, 'li[role="option"]')
                texts = [o.text.strip() for o in options if o.text.strip()]
                print(f"  ListBox {i}: {len(options)} opciones - {texts[:5]}")
        except Exception as e:
            print(f"METODO 2 - listboxes: Error - {str(e)[:80]}")
        
        # Metodo 3: buttons role option
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, 'button[role="option"]')
            print(f"\nMETODO 3 - buttons role='option': {len(buttons)} encontrados")
            if buttons:
                texts = [b.text.strip() for b in buttons[:10] if b.text.strip()]
                print(f"  Primeros textos: {texts}")
        except:
            print(f"METODO 3 - buttons: Error")
        
        # Metodo 4: inline twister
        try:
            twister = driver.find_element(By.ID, "inline-twister-row-size_name")
            print(f"\nMETODO 4 - inline twister: ENCONTRADO")
            items = twister.find_elements(By.CSS_SELECTOR, 'li.swatch-list-item-text')
            print(f"  Items: {len(items)}")
            texts = [it.text.strip() for it in items if it.text.strip()]
            print(f"  Textos: {texts[:10]}")
        except Exception as e:
            print(f"\nMETODO 4 - inline twister: NO ENCONTRADO")
            print(f"  Error: {str(e)[:80]}")
        
        # Metodo 5: Buscar por contenido "tamaño"
        try:
            size_elements = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'size')]")
            print(f"\nMETODO 5 - XPath 'size': {len(size_elements)} encontrados")
            if size_elements:
                texts = [e.text.strip()[:50] for e in size_elements[:5] if e.text.strip()]
                print(f"  Textos: {texts}")
        except:
            print(f"\nMETODO 5 - XPath: Error")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_amazon()

