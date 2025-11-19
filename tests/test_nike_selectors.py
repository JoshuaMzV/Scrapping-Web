from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

url = 'https://www.nike.com/es/w/nike-court-vision-low-next-nature-shoes-3q2xfq045'
print(f"Accediendo a: {url}")

try:
    driver.get(url)
    import time
    time.sleep(3)
    print("✓ Página cargada")
    
    # Verificar si tiene productTitle
    try:
        from selenium.webdriver.common.by import By
        elem = driver.find_element(By.ID, "productTitle")
        print(f"✓ productTitle encontrado: {elem.text[:50]}")
    except Exception as e:
        print(f"✗ productTitle no encontrado: {type(e).__name__}")
    
except Exception as e:
    print(f"Error al cargar: {e}")
finally:
    driver.quit()
