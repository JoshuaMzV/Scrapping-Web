#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test con URL específica de eBay que debe tener tallas numéricas reales
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')

from scrapers.nike import scrape_nike
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

# URL de eBay con product real que tiene tallas numéricas
EBAY_URL = "https://www.ebay.com/itm/236259481817"  # Nike shoes con tallas

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

try:
    print("="*60)
    print("Scrapeando eBay con tallas numéricas...")
    print("="*60)
    
    result = scrape_nike(driver, wait, EBAY_URL)
    
    if result:
        print("\n✅ Scraping completado")
        print(f"Nombre: {result['nombre'][:60]}")
        print(f"Precio: {result['precio']}")
        print(f"Tallas: {result['tallas']}")
        print(f"Sitio: {result['sitio']}")
    else:
        print("❌ No se pudo scrapear")
        
finally:
    driver.quit()
