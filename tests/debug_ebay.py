#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: Inspeccionar el HTML del producto eBay para encontrar dónde están las tallas
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    print("INSPECCIONANDO ESTRUCTURA DEL PRODUCTO")
    print("="*60)
    
    # Buscar TODOS los elementos con "button.listbox-button__control"
    buttons = driver.find_elements(By.CSS_SELECTOR, 'button.listbox-button__control')
    print(f"\n[1] Encontrados {len(buttons)} button.listbox-button__control")
    
    for idx, btn in enumerate(buttons):
        print(f"\n--- BOTÓN {idx + 1} ---")
        print(f"HTML: {btn.get_attribute('outerHTML')[:200]}")
        
        # Buscar label
        try:
            parent = btn.find_element(By.XPATH, '..')
            label = parent.find_element(By.CSS_SELECTOR, 'label, [class*="label"]')
            print(f"Label: {label.text}")
        except:
            print("Label: NO ENCONTRADO")
        
        # Click para abrir
        try:
            btn.click()
            time.sleep(0.5)
        except:
            try:
                driver.execute_script('arguments[0].click();', btn)
                time.sleep(0.5)
            except:
                pass
        
        # Buscar listbox abierto
        try:
            listboxes = driver.find_elements(By.CSS_SELECTOR, 'div[role="listbox"], ul[role="listbox"]')
            if listboxes:
                latest = listboxes[-1]
                options = latest.find_elements(By.CSS_SELECTOR, '[role="option"], .listbox__option')
                print(f"Opciones encontradas: {len(options)}")
                
                for opt_idx, opt in enumerate(options[:5]):  # Solo primeras 5
                    txt = opt.text.strip()
                    disabled = opt.get_attribute('aria-disabled')
                    print(f"  [{opt_idx}] '{txt}' (disabled={disabled})")
                    
                    # Inspeccionar HTML del option
                    html = opt.get_attribute('outerHTML')
                    print(f"       HTML: {html[:150]}")
        except Exception as e:
            print(f"Error al inspeccionar opciones: {str(e)[:50]}")
        
        # Cerrar listbox
        try:
            driver.execute_script('document.body.click();')
            time.sleep(0.3)
        except:
            pass
    
    print("\n" + "="*60)
    print("BUSCANDO OTROS SELECTORES")
    print("="*60)
    
    # Buscar select tradicional
    selects = driver.find_elements(By.CSS_SELECTOR, 'select')
    print(f"\n[2] Select tradicionales encontrados: {len(selects)}")
    for sel in selects:
        print(f"  ID: {sel.get_attribute('id')}")
        print(f"  Name: {sel.get_attribute('name')}")
    
    # Buscar divs con "listbox"
    listbox_divs = driver.find_elements(By.CSS_SELECTOR, 'div[role="listbox"]')
    print(f"\n[3] Div[role=listbox] en DOM: {len(listbox_divs)}")
    
    # Buscar spans con números
    print(f"\n[4] Buscando spans con números...")
    all_spans = driver.find_elements(By.TAG_NAME, 'span')
    size_spans = []
    for span in all_spans:
        txt = span.text.strip()
        if txt and any(c.isdigit() for c in txt) and len(txt) <= 5:
            size_spans.append(txt)
    
    print(f"Spans con números encontrados: {size_spans[:20]}")
    
finally:
    driver.quit()
