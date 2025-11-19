"""
Script de debug para verificar por qué no se extraen tallas en Nike.com y Amazon
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_nike_com():
    """Prueba específica para Nike.com"""
    print("\n" + "="*60)
    print("🧪 TESTING NIKE.COM TALLAS EXTRACTION")
    print("="*60)
    
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # URL de prueba: Nike Air Force 1
        url = "https://www.nike.com/w/mens-shoes-enndk"  # Página general para encontrar un producto
        print(f"\n📍 Navegando a: {url}")
        driver.get(url)
        time.sleep(3)
        
        # Buscar un producto disponible
        try:
            producto = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="product-card-link"]')
            producto_url = producto.get_attribute('href')
            print(f"✅ Producto encontrado: {producto_url}")
            driver.get(producto_url)
            time.sleep(2)
        except:
            print("❌ No se encontró producto individual")
            return
        
        # Intentar extraer tallas
        print("\n🔍 Buscando elementos de talla...")
        
        # Método 1: data-testid pdp-grid-selector-grid
        try:
            grid = driver.find_element(By.CSS_SELECTOR, '[data-testid="pdp-grid-selector-grid"]')
            print("✅ Encontrado: [data-testid='pdp-grid-selector-grid']")
            items = grid.find_elements(By.CSS_SELECTOR, '[data-testid="pdp-grid-selector-item"]')
            print(f"   → {len(items)} items encontrados")
            
            tallas = []
            for item in items:
                try:
                    cls = item.get_attribute('class') or ''
                    if 'disabled' in cls.lower():
                        continue
                    label = item.find_element(By.TAG_NAME, 'label').text.strip()
                    if label:
                        tallas.append(label)
                except:
                    pass
            
            if tallas:
                print(f"✅ Tallas extraídas: {', '.join(tallas)}")
            else:
                print("❌ No se extrajeron tallas de grid items")
        except Exception as e:
            print(f"❌ Error en grid selector: {str(e)[:80]}")
        
        # Método 2: Buscar select dropdown
        try:
            select = driver.find_element(By.CSS_SELECTOR, 'select[name*="size"]')
            print("✅ Encontrado: select con name='size'")
            options = select.find_elements(By.TAG_NAME, 'option')
            print(f"   → {len(options)} opciones")
        except:
            print("❌ No encontrado: select con name='size'")
        
        # Método 3: Buscar buttons con role=option
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, 'button[role="option"]')
            print(f"✅ Encontrado: {len(buttons)} buttons con role='option'")
            for btn in buttons[:5]:
                print(f"   → {btn.text}")
        except:
            print("❌ No encontrado: buttons con role='option'")
            
    finally:
        driver.quit()


def test_amazon():
    """Prueba específica para Amazon"""
    print("\n" + "="*60)
    print("🧪 TESTING AMAZON TALLAS EXTRACTION")
    print("="*60)
    
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)
    
    try:
        # URL de prueba
        url = "https://a.co/d/1a1b1c1d"  # Ejemplo - usaremos una URL real si es necesario
        print(f"\n📍 Navegando a: {url}")
        
        # Mejor: usar una URL de Nike en Amazon si la tienes
        # url = "https://www.amazon.com/s?k=nike+air+force+1"
        
        driver.get(url)
        time.sleep(2)
        
        print("\n🔍 Buscando elementos de talla en Amazon...")
        
        # Método 1: native_dropdown_selected_size_name
        try:
            select = driver.find_element(By.CSS_SELECTOR, '#native_dropdown_selected_size_name')
            print("✅ Encontrado: #native_dropdown_selected_size_name")
            options = select.find_elements(By.TAG_NAME, 'option')
            tallas = [o.text for o in options if o.text.strip() and 'seleccion' not in o.text.lower()]
            print(f"   → Tallas: {tallas}")
        except Exception as e:
            print(f"❌ Error en native_dropdown: {str(e)[:80]}")
        
        # Método 2: inline-twister-row-size_name
        try:
            twister = driver.find_element(By.ID, "inline-twister-row-size_name")
            print("✅ Encontrado: #inline-twister-row-size_name")
            items = twister.find_elements(By.CSS_SELECTOR, 'li.swatch-list-item-text')
            print(f"   → {len(items)} items")
        except Exception as e:
            print(f"❌ Error en twister: {str(e)[:80]}")
            
    finally:
        driver.quit()


if __name__ == "__main__":
    test_nike_com()
    test_amazon()
