from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

url = 'https://www.amazon.com/-/es/Nike-Air-Force-107-baloncesto/dp/B08QBJFKF3/ref=sr_1_1?sr=8-1&psc=1'

print('🔍 Scraping Amazon para debug de precio...')
driver.get(url)
time.sleep(3)

selectors = [
    ('span.aok-offscreen', 'aok-offscreen'),
    ('span.a-price-whole', 'a-price-whole'),
    ('.a-price-whole', '.a-price-whole'),
    ('span.a-price', 'a-price'),
]

for selector, desc in selectors:
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            print(f'\n✅ {desc}: encontrado {len(elements)} elementos')
            for i, el in enumerate(elements[:5]):
                text = el.text.strip()
                if text:
                    print(f'   [{i}] "{text}"')
        else:
            print(f'\n❌ {desc}: no encontrado')
    except Exception as e:
        print(f'\n❌ {desc}: error - {str(e)[:50]}')

print('\n' + '=' * 80)
print('Búsqueda general de cualquier elemento con precio...')
try:
    all_spans = driver.find_elements(By.TAG_NAME, 'span')
    print(f'Total de <span>: {len(all_spans)}')
    
    # Filtrar por aquellos que contengan números y $
    for span in all_spans[:20]:
        text = span.text.strip()
        if '$' in text or ('.' in text and len(text) < 20):
            print(f'  → "{text}"')
except:
    pass

driver.quit()
print('\n✅ Debug completado')
