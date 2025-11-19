from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(service=service, options=options)

url = 'https://www.amazon.com/-/es/Nike-Air-Force-107-baloncesto/dp/B08QBJFKF3/ref=sr_1_1?sr=8-1&psc=1'

print('🔍 Debug del precio capturado...')
driver.get(url)
time.sleep(3)

try:
    span_price = driver.find_element(By.CSS_SELECTOR, 'span.a-price')
    raw_text = span_price.text
    print(f'\nRaw text from span.a-price:')
    print(f'  repr: {repr(raw_text)}')
    print(f'  str: "{raw_text}"')
    
    precio_limpio = raw_text.replace('US$', '').strip()
    print(f'\nAfter replace and strip:')
    print(f'  repr: {repr(precio_limpio)}')
    print(f'  str: "{precio_limpio}"')
    
    import re
    precio_final = re.sub(r'[^\d.]', '', precio_limpio)
    print(f'\nAfter regex:')
    print(f'  repr: {repr(precio_final)}')
    print(f'  str: "{precio_final}"')
    print(f'  float: {float(precio_final)}')
    
except Exception as e:
    print(f'Error: {e}')

driver.quit()
