#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: Ver el HTML completo del listbox de tallas
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
    print("INSPECCIÓN DETALLADA DEL LISTBOX")
    print("="*60)
    
    # Encontrar botón de "US Shoe Size"
    buttons = driver.find_elements(By.CSS_SELECTOR, 'button.listbox-button__control')
    size_button = None
    
    for btn in buttons:
        try:
            parent = btn.find_element(By.XPATH, '..')
            label = parent.find_element(By.CSS_SELECTOR, 'label')
            if 'shoe size' in label.text.lower():
                size_button = btn
                print(f"Botón de talla encontrado: '{label.text}'")
                break
        except:
            pass
    
    if not size_button:
        # Intenta el segundo botón
        if len(buttons) > 1:
            size_button = buttons[1]
            print("Usando botón #2 (asumiendo que es 'US Shoe Size')")
    
    if size_button:
        # Click
        size_button.click()
        time.sleep(1)
        
        # Obtener listbox abierto
        listboxes = driver.find_elements(By.CSS_SELECTOR, 'div[role="listbox"]')
        print(f"\nListboxes encontrados: {len(listboxes)}")
        
        if listboxes:
            # Usar el último (el recién abierto)
            latest = listboxes[-1]
            
            print("\n--- HTML COMPLETO DEL LISTBOX ---")
            html = latest.get_attribute('outerHTML')
            print(html[:2000])
            
            print("\n--- OPCIONES DENTRO ---")
            options = latest.find_elements(By.CSS_SELECTOR, '[role="option"]')
            print(f"Encontradas {len(options)} opciones")
            
            for idx, opt in enumerate(options[:15]):
                print(f"\n[{idx}]")
                print(f"  text: '{opt.text}'")
                print(f"  data-sku-value-name: '{opt.get_attribute('data-sku-value-name')}'")
                opt_html = opt.get_attribute('outerHTML')
                print(f"  HTML: {opt_html[:300]}")

finally:
    driver.quit()
