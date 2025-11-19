#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug: Identificar qué botón es cuál
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
    
    buttons = driver.find_elements(By.CSS_SELECTOR, 'button.listbox-button__control')
    print(f"Total buttons: {len(buttons)}\n")
    
    for idx, btn in enumerate(buttons):
        print(f"=== BOTÓN {idx} ===")
        
        # Obtener label
        label_txt = ""
        try:
            # Método 1: buscar label en padre
            parent = btn.find_element(By.XPATH, '..')
            labels = parent.find_elements(By.CSS_SELECTOR, 'label, [class*="label"]')
            if labels:
                label_txt = labels[0].text
        except:
            pass
        
        if not label_txt:
            try:
                # Método 2: buscar texto antes del botón
                prev = btn.find_element(By.XPATH, './preceding-sibling::*[1]')
                label_txt = prev.text
            except:
                pass
        
        if not label_txt:
            # Método 3: obtener texto del botón mismo
            label_txt = btn.text or btn.get_attribute('aria-label') or "NO LABEL"
        
        print(f"Label: {label_txt}")
        print(f"aria-controls: {btn.get_attribute('aria-controls')}")
        print(f"value: {btn.get_attribute('value')}")
        
        # Click y ver qué abre
        btn.click()
        time.sleep(0.5)
        
        # Ver qué opciones tiene
        listboxes = driver.find_elements(By.CSS_SELECTOR, 'div[role="listbox"]')
        if listboxes:
            latest = listboxes[-1]
            options = latest.find_elements(By.CSS_SELECTOR, '[role="option"]')
            print(f"Opciones: {len(options)}")
            
            for opt in options[:3]:
                txt = ""
                try:
                    txt = opt.find_element(By.CSS_SELECTOR, 'span.listbox__value').text
                except:
                    txt = opt.text
                data_val = opt.get_attribute('data-sku-value-name')
                print(f"  - text: '{txt}' | data: '{data_val}'")
        
        # Cerrar
        driver.execute_script('document.body.click();')
        time.sleep(0.3)
        print()

finally:
    driver.quit()
