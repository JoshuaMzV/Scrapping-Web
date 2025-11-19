#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: Buscar donde están realmente las tallas con data-sku-value-name=7,8,8.5,etc
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
    print("BUSCANDO data-sku-value-name CON TALLAS")
    print("="*60)
    
    # Buscar todos los elementos con data-sku-value-name
    all_with_data = driver.find_elements(By.CSS_SELECTOR, '[data-sku-value-name]')
    print(f"\nEncontrados {len(all_with_data)} elementos con data-sku-value-name")
    
    for idx, elem in enumerate(all_with_data):
        val = elem.get_attribute('data-sku-value-name')
        tag = elem.tag_name
        cls = elem.get_attribute('class')
        role = elem.get_attribute('role')
        
        print(f"\n[{idx}] <{tag}> role='{role}' class='{cls}'")
        print(f"     value: '{val}'")
        
        # Ver su parent
        try:
            parent = elem.find_element(By.XPATH, '..')
            parent_tag = parent.tag_name
            parent_cls = parent.get_attribute('class')
            print(f"     parent: <{parent_tag}> class='{parent_cls}'")
        except:
            pass
    
    # Buscar específicamente por los valores "7", "8", "8.5", etc.
    print("\n" + "="*60)
    print("BÚSQUEDA ESPECÍFICA POR NÚMEROS DE TALLA")
    print("="*60)
    
    sizes_to_find = ['7', '8', '8.5', '9', '10', '11', '12']
    for size in sizes_to_find:
        elems = driver.find_elements(By.CSS_SELECTOR, f'[data-sku-value-name="{size}"]')
        print(f"data-sku-value-name='{size}': {len(elems)} elementos")
        
        if elems:
            elem = elems[0]
            tag = elem.tag_name
            print(f"  <{tag} data-sku-value-name='{size}'>")
            print(f"  HTML: {elem.get_attribute('outerHTML')[:200]}")

finally:
    driver.quit()
