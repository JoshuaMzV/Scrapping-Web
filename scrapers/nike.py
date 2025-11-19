"""
Scraper para productos NIKE
Detecta automáticamente el sitio (Nike.com, Amazon, eBay, etc.) y adapta el scraping
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# --- CONFIGURACIÓN DE COSTOS ---
PORCENTAJE_COSTO_CAJA = 8.0
PORCENTAJE_COSTO_ENVIO = 5.0
PORCENTAJE_SEGURO = 3.0

# --- CONFIGURACIÓN DE PRECIOS ---
TASA_CAMBIO_GTQ = 7.8
MULTIPLICADOR_PRECIO_MERCADO = 1.40
FACTOR_DESCUENTO_VENTA = 0.90


def scrape_nike_desde_nike_com(driver, wait, url):
    """Scraper específico para Nike.com"""
    try:
        driver.get(url)
        time.sleep(1)
        
        # Cerrar pop-ups
        popup_selectors = [
            '[data-testid="modal-close-button"]',
            'button[aria-label="Close"]',
            'button[aria-label*="Cerrar"]',
            'button[title="Close"]',
        ]

        for attempt in range(3):
            closed_any = False
            for sel in popup_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, sel)
                    for b in buttons:
                        try:
                            if b.is_displayed() and b.is_enabled():
                                b.click()
                                closed_any = True
                                time.sleep(0.3)
                        except:
                            pass
                except:
                    pass
            if not closed_any:
                break

        wait.until(EC.presence_of_element_located((By.ID, "pdp_product_title")))
        
        nombre = driver.find_element(By.ID, "pdp_product_title").text
        precio_str = driver.find_element(By.CSS_SELECTOR, '[data-testid="currentPrice-container"]').text
        imagen = driver.find_element(By.CSS_SELECTOR, 'img[src^="https://static.nike.com/a/images/"]').get_attribute('src')
        
        # Extracción de tallas - MÉTODO 1: grid-selector
        tallas = "No encontradas"
        try:
            grid_tallas = driver.find_element(By.CSS_SELECTOR, '[data-testid="pdp-grid-selector-grid"]')
            size_divs = grid_tallas.find_elements(By.CSS_SELECTOR, '[data-testid="pdp-grid-selector-item"]')
            available = []
            for div in size_divs:
                try:
                    cls = div.get_attribute('class') or ''
                    if 'disabled' in cls.lower():
                        continue
                    try:
                        input_el = div.find_element(By.TAG_NAME, 'input')
                        if (input_el.get_attribute('aria-disabled') or '').lower() == 'true':
                            continue
                    except:
                        pass
                    try:
                        label = div.find_element(By.TAG_NAME, 'label').text.strip()
                    except:
                        label = div.text.strip() or ''
                    if label:
                        available.append(label)
                except:
                    pass
            if available:
                tallas = ', '.join(available)
        except:
            pass
        
        # MÉTODO 2: Si no encontró tallas, intentar con buttons role=option
        if tallas == "No encontradas":
            try:
                size_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[role="option"]')
                available = []
                for btn in size_buttons:
                    try:
                        aria_selected = btn.get_attribute('aria-selected') or 'false'
                        if aria_selected.lower() == 'true':
                            continue
                        aria_disabled = btn.get_attribute('aria-disabled') or 'false'
                        if aria_disabled.lower() == 'true':
                            continue
                        txt = btn.text.strip()
                        if txt and txt.upper() != 'SELECCIONAR':
                            available.append(txt)
                    except:
                        pass
                if available:
                    tallas = ', '.join(available)
            except:
                pass
        
        # MÉTODO 3: Si aún no encuentra, intentar con select nativo
        if tallas == "No encontradas":
            try:
                select_el = driver.find_element(By.CSS_SELECTOR, 'select[name*="size"]')
                options = select_el.find_elements(By.TAG_NAME, 'option')
                available = []
                for opt in options:
                    txt = opt.text.strip()
                    if txt and txt.upper() != 'SELECCIONAR':
                        available.append(txt)
                if available:
                    tallas = ', '.join(available)
            except:
                pass
        
        return {"nombre": nombre, "precio": precio_str, "imagen": imagen, "tallas": tallas, "sitio": "Nike.com"}
    except Exception as e:
        print(f"    ❌ Error en Nike.com: {str(e)[:50]}")
        return None


def scrape_nike_desde_amazon(driver, wait, url):
    """Scraper para productos Nike en Amazon"""
    try:
        driver.get(url)
        time.sleep(2)

        nombre = driver.find_element(By.ID, "productTitle").text
        
        precio_str = "Error"
        try:
            # Obtener elemento con precio
            precio_elem = driver.find_element(By.CSS_SELECTOR, '.a-price')
            precio_str = precio_elem.text.strip().replace('\n', '.')
        except:
            pass

        imagen = driver.find_element(By.ID, "landingImage").get_attribute('src')
        
        tallas = "No encontradas"
        
        # Buscar select nativo de tallas
        try:
            select_el = driver.find_element(By.CSS_SELECTOR, '#native_dropdown_selected_size_name')
            options = select_el.find_elements(By.TAG_NAME, 'option')
            avail = []
            for o in options:
                txt = o.text.strip()
                if txt and txt.lower() != 'seleccionar':
                    avail.append(txt)
            if avail:
                tallas = ', '.join(avail)
        except:
            pass

        return {"nombre": nombre, "precio": precio_str, "imagen": imagen, "tallas": tallas, "sitio": "Amazon"}
    except Exception as e:
        print(f"    ❌ Error en Amazon: {str(e)[:50]}")
        return None


def scrape_nike_desde_ebay(driver, wait, url):
    """Scraper para productos Nike en eBay - LÓGICA MEJORADA PARA DETECTAR TALLAS"""
    try:
        driver.get(url)
        time.sleep(2)

        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.x-item-title__mainTitle span')))
        nombre = driver.find_element(By.CSS_SELECTOR, 'h1.x-item-title__mainTitle span').text
        
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.x-price-primary span.ux-textspans')))
        precio_str = driver.find_element(By.CSS_SELECTOR, 'div.x-price-primary span.ux-textspans').text
        
        imagen = "No encontrada"
        try:
            imagen = driver.find_element(By.CSS_SELECTOR, 'img[src*="ebayimg.com"]').get_attribute('src')
        except:
            pass
        
        tallas = "No encontradas"
        try:
            # Buscar TODOS los botones de control (puede haber color, talla, etc.)
            buttons = driver.find_elements(By.CSS_SELECTOR, 'button.listbox-button__control')
            print(f"    → Encontrados {len(buttons)} option panes en eBay")
            
            # Palabras clave para identificar si un pane es de TALLAS
            size_keywords = ['size', 'talla', 'shoe size', 'shoe', 'taille', 'uk', 'us', 'eu']
            # Palabras clave a IGNORAR (no son tallas)
            ignore_keywords = ['color', 'colour', 'style', 'material', 'condition', 'format', 'brand']
            
            # Recorrer cada botón para encontrar el de tallas
            for btn_idx, btn in enumerate(buttons):
                try:
                    # Obtener label/nombre del control
                    label_text = ""
                    try:
                        # Buscar label asociado al botón
                        parent = btn.find_element(By.XPATH, '..')
                        label_elem = parent.find_element(By.CSS_SELECTOR, 'label, [class*="label"]')
                        label_text = label_elem.text.lower().strip()
                    except:
                        try:
                            # Fallback: obtener texto anterior al botón
                            label_text = btn.find_element(By.XPATH, './preceding-sibling::*[1]').text.lower().strip()
                        except:
                            pass
                    
                    # Limpiar label (remover ":" al final)
                    label_text = label_text.rstrip(':').strip()
                    
                    print(f"    → Pane {btn_idx + 1}: '{label_text}'", end="")
                    
                    # DECIDIR: ¿Es este pane de TALLAS?
                    is_size_pane = False
                    
                    # Si tiene palabra clave de TAMAÑO
                    if any(keyword in label_text for keyword in size_keywords):
                        is_size_pane = True
                        print(" ✅ ES TALLA")
                    # Si tiene palabra clave a IGNORAR
                    elif any(keyword in label_text for keyword in ignore_keywords):
                        print(" ❌ NO ES TALLA")
                        continue
                    else:
                        # Si no sabemos, saltar
                        print(" ? INCIERTO - SALTANDO")
                        continue
                    
                    # Si llegamos aquí, ES un pane de TALLAS
                    if is_size_pane:
                        # Click en el botón para abrir las opciones
                        try:
                            btn.click()
                            time.sleep(0.5)
                        except:
                            try:
                                driver.execute_script('arguments[0].click();', btn)
                                time.sleep(0.5)
                            except:
                                continue
                        
                        # Esperar a que aparezca el listbox correcto
                        try:
                            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[role="listbox"], ul[role="listbox"]')), timeout=2)
                        except:
                            pass
                        
                        # Obtener el listbox correcto
                        # Criterio: el que tenga opciones con números en data-sku-value-name
                        all_listboxes = driver.find_elements(By.CSS_SELECTOR, 'div[role="listbox"], ul[role="listbox"]')
                        target_listbox = None
                        
                        for listbox in all_listboxes:
                            # Buscar opciones con números en data-sku-value-name
                            options_with_data = listbox.find_elements(By.CSS_SELECTOR, '[role="option"][data-sku-value-name]')
                            
                            # Ver si alguno tiene números
                            has_size_options = False
                            for opt in options_with_data:
                                data_val = opt.get_attribute('data-sku-value-name')
                                if data_val and any(char.isdigit() for char in data_val):
                                    has_size_options = True
                                    break
                            
                            if has_size_options:
                                target_listbox = listbox
                                break
                        
                        if not target_listbox:
                            # Fallback: usar el último listbox
                            if all_listboxes:
                                target_listbox = all_listboxes[-1]
                        
                        # Extraer valores disponibles - VALIDAR QUE CONTENGAN NÚMEROS
                        available_sizes_text = []
                        if target_listbox:
                            options = target_listbox.find_elements(By.CSS_SELECTOR, '[role="option"]')
                            print(f"    → Encontradas {len(options)} opciones")
                            for option in options:
                                try:
                                    aria = option.get_attribute('aria-disabled')
                                    tabindex = option.get_attribute('tabindex')
                                    
                                    # SOLO ignorar opciones DESHABILITADAS
                                    if aria == 'true' or (tabindex is not None and tabindex.strip() == '-1'):
                                        continue
                                    
                                    # Intentar extraer texto de varias formas (PRIORIDAD: data-sku-value-name)
                                    txt = ""
                                    
                                    # PRIORIDAD 1: data-sku-value-name (donde eBay guarda las tallas reales)
                                    txt = option.get_attribute('data-sku-value-name') or ""
                                    txt = txt.strip()
                                    
                                    # PRIORIDAD 2: span.listbox__value
                                    if not txt:
                                        try:
                                            span = option.find_element(By.CSS_SELECTOR, 'span.listbox__value')
                                            txt = span.text.strip()
                                        except:
                                            pass
                                    
                                    # PRIORIDAD 3: innerText del option
                                    if not txt:
                                        txt = option.text.strip()
                                    
                                    # PRIORIDAD 4: ejecutar JS para obtener texto
                                    if not txt:
                                        try:
                                            txt = driver.execute_script('return arguments[0].innerText', option).strip()
                                        except:
                                            pass
                                    
                                    # Filtro: ignorar "Select", vacíos y valores SIN NÚMEROS
                                    if not txt or 'select' in txt.lower():
                                        continue
                                    
                                    # VALIDACIÓN CRÍTICA: Debe contener al menos un NÚMERO
                                    # Las tallas reales son: "5", "6", "7.5", "8", "9M", "10W", etc.
                                    # No deben ser: "Positivas", "Negativas", "Neutrales", "Color", etc.
                                    has_digit = any(char.isdigit() for char in txt)
                                    if not has_digit:
                                        print(f"       ⊘ Ignorando valor sin números: '{txt}'")
                                        continue
                                    
                                    txt = txt.replace('(Out of stock)', '').strip()
                                    
                                    if txt and txt not in available_sizes_text:
                                        available_sizes_text.append(txt)
                                except:
                                    continue
                        
                        # Si encontramos valores en este pane de TALLAS, guardarlos y salir
                        if available_sizes_text:
                            tallas = ", ".join(available_sizes_text)
                            print(f"    ✅ Tallas capturadas: {tallas[:80]}")
                            break  # Salir del loop de botones - encontramos las tallas
                        
                        # Cerrar el listbox
                        try:
                            driver.execute_script('document.body.click();')
                            time.sleep(0.3)
                        except:
                            pass
                
                except Exception as e:
                    print(f"    ❌ Error procesando pane {btn_idx + 1}: {str(e)[:30]}")
                    continue

        except Exception as e:
            print(f"    → Error en búsqueda de tallas: {str(e)[:50]}")
            pass

        return {"nombre": nombre, "precio": precio_str, "imagen": imagen, "tallas": tallas, "sitio": "eBay"}
    except Exception as e:
        print(f"    ❌ Error en eBay: {str(e)[:50]}")
        return None


def scrape_nike(driver, wait, url):
    """
    Scraper inteligente para Nike que detecta el sitio automáticamente
    y usa el scraper específico
    """
    print(f"    🔍 Detectando sitio...", end="")
    
    if "nike.com" in url.lower():
        print(" Nike.com")
        return scrape_nike_desde_nike_com(driver, wait, url)
    elif "amazon" in url.lower():
        print(" Amazon")
        return scrape_nike_desde_amazon(driver, wait, url)
    elif "ebay" in url.lower():
        print(" eBay")
        return scrape_nike_desde_ebay(driver, wait, url)
    else:
        print(" Sitio desconocido")
        return None


def calcular_precios(precio_usd):
    """Calcula los precios y ganancias"""
    try:
        precio_usd = float(precio_usd)
    except (ValueError, TypeError):
        precio_usd = 0.0

    costo_caja = precio_usd * (PORCENTAJE_COSTO_CAJA / 100)
    costo_envio = precio_usd * (PORCENTAJE_COSTO_ENVIO / 100)
    subtotal = precio_usd + costo_caja + costo_envio
    costo_seguro = subtotal * (PORCENTAJE_SEGURO / 100)
    costo_final_usd = subtotal + costo_seguro
    
    precio_mercado_gtq = (precio_usd * MULTIPLICADOR_PRECIO_MERCADO) * TASA_CAMBIO_GTQ 
    precio_venta_gtq = precio_mercado_gtq * FACTOR_DESCUENTO_VENTA
    
    costo_final_gtq = costo_final_usd * TASA_CAMBIO_GTQ
    ganancia_gtq = precio_venta_gtq - costo_final_gtq
    margen_ganancia = (ganancia_gtq / precio_venta_gtq) * 100 if precio_venta_gtq > 0 else 0

    return {
        "Precio Original (USD)": round(precio_usd, 2),
        "Costo Final por Unidad (USD)": round(costo_final_usd, 2),
        "Costo Final por Unidad (GTQ)": round(costo_final_gtq, 2),
        "Precio Sugerido Venta (GTQ)": round(precio_venta_gtq, 2),
        "Ganancia por Unidad (GTQ)": round(ganancia_gtq, 2),
        "Margen de Ganancia (%)": round(margen_ganancia, 2),
    }


def limpiar_precio(precio_str):
    """Limpia el string de precio"""
    # Reemplazar coma por punto (para locales que usan coma como decimal)
    precio_limpio = precio_str.replace(',', '.')
    # Remover todo excepto dígitos y puntos
    precio_limpio = re.sub(r'[^\d.]', '', precio_limpio)
    try:
        return float(precio_limpio)
    except:
        return 0.0
