from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Chrome(service=service, options=options)

url = 'https://www.nike.com/es/t/air-force-1-07-zapatillas-E5NnNyBr/CW2288-111'

print('🔍 Debug del precio Nike.com...')
driver.get(url)
time.sleep(3)

try:
    span_price = driver.find_element(By.CSS_SELECTOR, '[data-testid="currentPrice-container"]')
    raw_text = span_price.text
    print(f'Raw text from Nike price:')
    print(f'  repr: {repr(raw_text)}')
    print(f'  str: "{raw_text}"')
    
except Exception as e:
    print(f'Error: {e}')

driver.quit()
