#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug avanzado: Buscar las tallas en OTROS elementos del página
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

EBAY_URL = "https://www.ebay.com/itm/357896320478"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

try:
    driver.get(EBAY_URL)
    time.sleep(3)
    
    print("="*60)
    print("BÚSQUEDA AVANZADA DE TALLAS")
    print("="*60)
    
    # [1] Buscar en data attributes
    print("\n[1] Buscando en data-sku-value-name...")
    options_with_data = driver.find_elements(By.CSS_SELECTOR, '[data-sku-value-name]')
    print(f"Encontrados: {len(options_with_data)}")
    for opt in options_with_data[:10]:
        val = opt.get_attribute('data-sku-value-name')
        print(f"  - {val}")
    
    # [2] Buscar todos los elementos con role="option"
    print("\n[2] Todos los [role=option] en la página...")
    all_options = driver.find_elements(By.CSS_SELECTOR, '[role="option"]')
    print(f"Encontrados: {len(all_options)}")
    
    for idx, opt in enumerate(all_options):
        txt = opt.text.strip()
        data_val = opt.get_attribute('data-sku-value-name')
        aria = opt.get_attribute('aria-selected')
        print(f"  [{idx}] text='{txt}' | data='{data_val}' | aria-selected={aria}")
    
    # [3] Buscar en el control de "US Shoe Size" específicamente
    print("\n[3] Enfoque en control 'US Shoe Size'...")
    size_button = None
    buttons = driver.find_elements(By.CSS_SELECTOR, 'button.listbox-button__control')
    for btn in buttons:
        try:
            parent = btn.find_element(By.XPATH, '..')
            label = parent.find_element(By.CSS_SELECTOR, 'label')
            if 'shoe size' in label.text.lower():
                size_button = btn
                print(f"Encontrado botón de talla: '{label.text}'")
                break
        except:
            pass
    
    if size_button:
        # Click y esperar
        try:
            size_button.click()
            time.sleep(1)
        except:
            driver.execute_script('arguments[0].click();', size_button)
            time.sleep(1)
        
        # Buscar el listbox que se abrió
        listboxes = driver.find_elements(By.CSS_SELECTOR, 'div[role="listbox"], ul[role="listbox"]')
        print(f"Listboxes encontrados: {len(listboxes)}")
        
        if listboxes:
            latest_listbox = listboxes[-1]
            print(f"Inspeccionando último listbox...")
            print(f"HTML: {latest_listbox.get_attribute('outerHTML')[:500]}")
            
            # Buscar opciones
            options = latest_listbox.find_elements(By.CSS_SELECTOR, '[role="option"]')
            print(f"Opciones en listbox: {len(options)}")
            
            for opt_idx, opt in enumerate(options):
                print(f"\n  Opción {opt_idx}:")
                print(f"    text: '{opt.text}'")
                print(f"    innerText: {opt.get_attribute('innerText')}")
                print(f"    data-sku-value-name: {opt.get_attribute('data-sku-value-name')}")
                
                # Buscar todos los spans dentro
                spans = opt.find_elements(By.TAG_NAME, 'span')
                for span in spans:
                    span_txt = span.text.strip()
                    if span_txt:
                        print(f"    span: '{span_txt}'")
                
                # Datos del elemento
                print(f"    HTML: {opt.get_attribute('outerHTML')[:250]}")
    
    # [4] Búsqueda global de números que parecen tallas
    print("\n[4] Búsqueda de patrones de talla (números 5-13)...")
    all_text = driver.find_element(By.TAG_NAME, 'body').text
    import re
    sizes = re.findall(r'\b([5-9]|1[0-3])(\.5)?\b', all_text)
    print(f"Números encontrados: {set(sizes) if sizes else 'Ninguno'}")
    
finally:
    driver.quit()
