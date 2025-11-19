import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# --- ================================================================= ---
# ---   SECCIÓN DE CONFIGURACIÓN (LA MISMA QUE ANTES)               ---
# --- ================================================================= ---

# --- Costos Variables como Porcentaje del Precio del Producto ---
PORCENTAJE_COSTO_CAJA = 8.0
PORCENTAJE_COSTO_ENVIO = 5.0
PORCENTAJE_SEGURO = 3.0

# --- Estrategia de Precios para el Mercado Local (Guatemala) ---
TASA_CAMBIO_GTQ = 7.8
MULTIPLICADOR_PRECIO_MERCADO = 1.40
FACTOR_DESCUENTO_VENTA = 0.90

# --- ================================================================= ---
# ---     FUNCIONES DE SCRAPING (UNA PARA CADA SITIO WEB)           ---
# --- ================================================================= ---

def scrape_nike(driver, wait, url):
    """Función para extraer datos de Nike.com con manejo de pop-ups CORREGIDO."""
    try:
        driver.get(url)
        # --- Intentar cerrar varios pop-ups/modales que pueden aparecer (iterativo) ---
        popup_selectors = [
            '[data-testid="modal-close-button"]',
            'button[aria-label="Close"]',
            'button[aria-label*="Cerrar"]',
            'button[title="Close"]',
            '.modal-close',
            '.close',
            '[data-dismiss="modal"]',
            '[aria-label*="close"]',
            '[data-testid*="close"]'
        ]

        # Intentar hasta N veces para que, si aparecen varios modales secuenciales, los cerremos todos
        for attempt in range(5):
            closed_any = False
            for sel in popup_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, sel)
                    for b in buttons:
                        try:
                            if b.is_displayed() and b.is_enabled():
                                b.click()
                                closed_any = True
                                print(f"    -> Cerrado pop-up con selector: {sel}")
                                time.sleep(0.5)
                        except Exception:
                            # ignorar errores al clickear un botón en particular
                            continue
                except Exception:
                    continue
            if not closed_any:
                break

        wait.until(EC.presence_of_element_located((By.ID, "pdp_product_title")))
        
        nombre = driver.find_element(By.ID, "pdp_product_title").text
        precio_str = driver.find_element(By.CSS_SELECTOR, '[data-testid="currentPrice-container"]').text
        imagen = driver.find_element(By.CSS_SELECTOR, 'img[src^="https://static.nike.com/a/images/"]').get_attribute('src')
        
        # --- Extracción de tallas con validación robusta ---
        tallas = "No encontradas"
        try:
            grid_tallas = driver.find_element(By.CSS_SELECTOR, '[data-testid="pdp-grid-selector-grid"]')
            size_divs = grid_tallas.find_elements(By.CSS_SELECTOR, '[data-testid="pdp-grid-selector-item"]')
            available = []
            for div in size_divs:
                try:
                    cls = div.get_attribute('class') or ''
                    # ignorar si el contenedor tiene clase 'disabled'
                    if 'disabled' in cls.lower():
                        continue

                    # intentar obtener input y verificar atributos que indiquen no disponible
                    try:
                        input_el = div.find_element(By.TAG_NAME, 'input')
                        aria_disabled = (input_el.get_attribute('aria-disabled') or '').lower() == 'true'
                        disabled_attr = input_el.get_attribute('disabled') is not None
                        if aria_disabled or disabled_attr:
                            continue
                    except Exception:
                        # si no existe input, seguir y tratar de leer label
                        pass

                    # obtener texto de label (si existe)
                    try:
                        label = div.find_element(By.TAG_NAME, 'label').text.strip()
                    except Exception:
                        label = div.text.strip() or ''

                    if label:
                        available.append(label)
                except Exception:
                    continue
            if available:
                tallas = ', '.join(available)
        except Exception as e:
            print(f"    -> No se pudieron extraer tallas de Nike (selector ausente o cambiado): {e}")
        
        return {"nombre": nombre, "precio": precio_str, "imagen": imagen, "tallas": tallas}
    except Exception as e:
        print(f"    -> ERROR en Nike: {e}")
        return {"nombre": "Error", "precio": "Error", "imagen": "Error", "tallas": "Error"}

def scrape_amazon(driver, wait, url):
    """Función para extraer datos de Amazon.com (versión anti-detección)."""
    try:
        driver.get(url)
        time.sleep(3)

        wait.until(EC.visibility_of_element_located((By.ID, "productTitle")))
        nombre = driver.find_element(By.ID, "productTitle").text
        
        precio_str = "Error"
        try:
            precio_str = driver.find_element(By.CSS_SELECTOR, 'span.aok-offscreen').text
        except:
            try:
                precio_str = driver.find_element(By.CSS_SELECTOR, 'span.a-price-whole').text
            except:
                precio_str = driver.find_element(By.CSS_SELECTOR, '.a-price.aok-align-center').text

        imagen = driver.find_element(By.ID, "landingImage").get_attribute('src')
        
        tallas = "No encontradas"

        # 1) Intentar select nativo (caso que compartiste con id 'native_dropdown_selected_size_name')
        try:
            select_el = driver.find_element(By.CSS_SELECTOR, '#native_dropdown_selected_size_name')
            options = select_el.find_elements(By.TAG_NAME, 'option')
            avail = []
            for o in options:
                try:
                    txt = o.text.strip()
                    cls = (o.get_attribute('class') or '').lower()
                    val = o.get_attribute('value') or ''
                    # ignorar opción vacía o 'Seleccionar'
                    if not txt or 'seleccion' in txt.lower():
                        continue
                    # ignorar opciones marcadas como unavailable por clase
                    if 'dropdownunavailable' in cls.replace(' ', ''):
                        continue
                    # ignorar options con value que no parezca talla (opcional)
                    avail.append(txt)
                except Exception:
                    continue
            if avail:
                tallas = ', '.join(avail)
        except Exception:
            # 2) Fallback: buscar listbox popover refinado (evitar listas de departamentos)
            try:
                listbox_candidates = driver.find_elements(By.CSS_SELECTOR, 'ul[role="listbox"]')
                found = False
                for listbox in listbox_candidates:
                    try:
                        options = listbox.find_elements(By.CSS_SELECTOR, 'li[role="option"]')
                        looks_like_size = False
                        for li in options:
                            lid = (li.get_attribute('id') or '').lower()
                            lcls = (li.get_attribute('class') or '').lower()
                            if lid.startswith('size_name_') or 'dropdown-item' in lcls or 'dropdownavailable' in lcls or 'dropdownunavailable' in lcls:
                                looks_like_size = True
                                break
                        if not looks_like_size:
                            continue

                        avail2 = []
                        for li in options:
                            try:
                                lcls = (li.get_attribute('class') or '').lower()
                                if 'dropdownunavailable' in lcls.replace(' ', ''):
                                    continue
                                try:
                                    text = li.find_element(By.CSS_SELECTOR, 'a').text.strip()
                                except Exception:
                                    text = li.text.strip()
                                if text and 'seleccion' not in text.lower():
                                    avail2.append(text)
                            except Exception:
                                continue
                        if avail2:
                            tallas = ', '.join(avail2)
                            found = True
                            break
                    except Exception:
                        continue
                if not found:
                    # 3) Fallback final: inline twister (existente)
                    try:
                        wait.until(EC.visibility_of_element_located((By.ID, "inline-twister-row-size_name")))
                        size_list_container = driver.find_element(By.ID, "inline-twister-row-size_name")
                        size_items = size_list_container.find_elements(By.CSS_SELECTOR, 'li.swatch-list-item-text')
                        available_sizes_text = []
                        for item in size_items:
                            item_cls = (item.get_attribute('class') or '').lower()
                            if 'a-button-unavailable' not in item_cls:
                                try:
                                    size_text_element = item.find_element(By.CSS_SELECTOR, 'span.swatch-title-text-display')
                                    available_sizes_text.append(size_text_element.text.strip())
                                except Exception:
                                    if item.text.strip():
                                        available_sizes_text.append(item.text.strip())
                        if available_sizes_text:
                            tallas = ", ".join(available_sizes_text)
                    except Exception:
                        pass
            except Exception:
                pass

        return {"nombre": nombre, "precio": precio_str, "imagen": imagen, "tallas": tallas}
    except Exception as e:
        print(f"    -> ERROR en Amazon: {e}")
        return {"nombre": "Error", "precio": "Error", "imagen": "Error", "tallas": "Error"}

def scrape_ebay(driver, wait, url):
    """Función para extraer datos de eBay.com (NUEVA LÓGICA IMPLEMENTADA)."""
    try:
        driver.get(url)
        time.sleep(2) # Pequeña pausa para eBay

        # --- Extracción de Datos (SELECTORES DE EBAY) ---
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1.x-item-title__mainTitle span')))
        nombre = driver.find_element(By.CSS_SELECTOR, 'h1.x-item-title__mainTitle span').text
        
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.x-price-primary span.ux-textspans')))
        precio_str = driver.find_element(By.CSS_SELECTOR, 'div.x-price-primary span.ux-textspans').text
        
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'img[src*="ebayimg.com"]')))
        imagen = driver.find_element(By.CSS_SELECTOR, 'img[src*="ebayimg.com"]').get_attribute('src')
        
        # --- Lógica de Tallas de eBay (click en control + extracción) ---
        tallas = "No encontradas"
        try:
            # Intentar click en el control que abre el listbox
            print("    -> Intentando abrir control de tallas en eBay...")
            opened = False
            # 1) click normal
            try:
                btn = driver.find_element(By.CSS_SELECTOR, 'button.listbox-button__control')
                print(f"    -> Found button.listbox-button__control, displayed={btn.is_displayed()}, enabled={btn.is_enabled()}")
                try:
                    btn.click()
                    opened = True
                    print("    -> Click normal realizado en botón de eBay.")
                except Exception as err:
                    print(f"    -> Click normal falló: {err}")
            except Exception:
                print("    -> button.listbox-button__control no encontrado.")

            # 2) intentar click por JS si normal falló
            if not opened:
                try:
                    driver.execute_script('arguments[0].click();', btn)
                    opened = True
                    print("    -> Click via JS realizado.")
                except Exception as err:
                    print(f"    -> Click via JS falló: {err}")

            # 3) intentar scroll y click con ActionChains
            if not opened:
                try:
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(btn).click().perform()
                    opened = True
                    print("    -> Click via ActionChains realizado.")
                except Exception as err:
                    print(f"    -> ActionChains click falló: {err}")

            # 4) intentar click en el elemento padre si existe
            if not opened:
                try:
                    parent = driver.find_element(By.CSS_SELECTOR, '.listbox-button')
                    driver.execute_script('arguments[0].scrollIntoView(true);', parent)
                    parent.click()
                    opened = True
                    print("    -> Click realizado en padre .listbox-button")
                except Exception as err:
                    print(f"    -> Click en padre falló: {err}")

            # Esperar por el listbox (puede usar role=listbox)
            print("    -> Esperando aparición del listbox (role=listbox)...")
            try:
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[role="listbox"], ul[role="listbox"]')))
            except Exception as e_wait:
                print(f"    -> Timeout esperando listbox: {repr(e_wait)}")

            # Inspeccionar candidatos a listbox para diagnóstico
            candidates = driver.find_elements(By.CSS_SELECTOR, 'div[role="listbox"], ul[role="listbox"]')
            print(f"    -> Encontrados {len(candidates)} candidatos a listbox en la página." )
            for i, c in enumerate(candidates[:5], start=1):
                try:
                    cid = c.get_attribute('id') or '<no-id>'
                    ccls = c.get_attribute('class') or '<no-class>'
                    ctext = c.text.strip().replace('\n', ' ')[:120]
                    print(f"      - candidato {i}: id={cid}, class={ccls}, text_preview='{ctext}'")
                except Exception as e_c:
                    print(f"      - candidato {i}: error leyendo atributos: {e_c}")

            # Preferir el candidato a listbox que contenga más opciones válidas
            options_container = None
            options = []
            try:
                # Reusar los candidatos ya indexados arriba si existen
                all_candidates = driver.find_elements(By.CSS_SELECTOR, 'div[role="listbox"], ul[role="listbox"], div.listbox__options, .listbox__options')
                best = None
                best_count = 0
                for c in all_candidates:
                    try:
                        opts = c.find_elements(By.CSS_SELECTOR, '[role="option"], .listbox__option')
                        if len(opts) > best_count:
                            best = c
                            best_count = len(opts)
                    except Exception:
                        continue
                if best is not None and best_count > 0:
                    options_container = best
                    options = options_container.find_elements(By.CSS_SELECTOR, '[role="option"], .listbox__option')
                    print(f"    -> Seleccionado options_container candidato con id='{options_container.get_attribute('id')}' class='{options_container.get_attribute('class')}' y {len(options)} opciones.")
                else:
                    # Fallback global: buscar .listbox__option o role=option en todo el documento
                    options = driver.find_elements(By.CSS_SELECTOR, '.listbox__option, [role="option"]')
                    print(f"    -> Fallback global: encontradas {len(options)} opciones buscando '.listbox__option, [role=\"option\"]' en documento.")
                    if options:
                        options_container = None
                    else:
                        print('    -> No se encontraron opciones en candidates ni globalmente')
                        options = []
            except Exception as e_opt:
                print(f"    -> Error localizando options_container/opciones: {repr(e_opt)}")
                options = []
            available_sizes_text = []
            if options:
                for idx, option in enumerate(options, start=1):
                    try:
                        aria = option.get_attribute('aria-disabled')
                        tabindex = option.get_attribute('tabindex')
                        data_name = option.get_attribute('data-sku-value-name') or option.get_attribute('data-value') or ''
                        try:
                            span = option.find_element(By.CSS_SELECTOR, 'span.listbox__value')
                            txt = span.text.strip()
                        except Exception:
                            txt = option.text.strip()
                        print(f"      option {idx}: aria-disabled={aria}, tabindex={tabindex}, data_name='{data_name}', text='{txt[:80]}'")
                        # ignorar opciones deshabilitadas: aria-disabled='true' o tabindex='-1'
                        if aria == 'true' or (tabindex is not None and tabindex.strip() == '-1'):
                            print(f"        -> opción {idx} marcada como deshabilitada, se ignora.")
                            continue
                        if not txt or 'select' in txt.lower():
                            continue
                        txt = txt.replace('(Out of stock)', '').strip()
                        if txt:
                            available_sizes_text.append(txt)
                    except Exception as e_opt:
                        print(f"      -> error procesando option {idx}: {repr(e_opt)}")
                        continue

            # Fallback: si existe un select oculto con opciones nativas
            if not available_sizes_text and options_container is not None:
                try:
                    native_select = options_container.find_element(By.CSS_SELECTOR, 'select.listbox__native')
                    opts = native_select.find_elements(By.TAG_NAME, 'option')
                    for o in opts:
                        try:
                            t = o.text.strip()
                            if t and 'select' not in t.lower():
                                available_sizes_text.append(t)
                        except Exception:
                            continue
                except Exception:
                    pass

            if available_sizes_text:
                tallas = ", ".join(available_sizes_text)

        except Exception as e:
            print(f"    -> No se pudieron extraer las tallas de eBay: {e}")

        return {"nombre": nombre, "precio": precio_str, "imagen": imagen, "tallas": tallas}
    except Exception as e:
        print(f"    -> ERROR en eBay: {e}")
        return {"nombre": "Error", "precio": "Error", "imagen": "Error", "tallas": "Error"}

# --- ================================================================= ---
# ---                  LÓGICA PRINCIPAL DEL SCRIPT                   ---
# --- ================================================================= ---

# Lista de URLs de diferentes sitios
urls_a_raspar = [
    # Nike
    "https://www.nike.com/us/es/t/tenis-air-jordan5-retro-medium-soft-pink-PLAgkkji/HQ7978-102",
    # Amazon
    "https://www.amazon.com/-/es/Zapatos-Vision-Nature-hombre-Blanco/dp/B0983LWFXT",
    # eBay (AHORA INCLUIDO)
    "https://www.ebay.com/itm/336174071808?_skw=nike+air+force+1&itmmeta=01K7MMTP6VWV85PK4XWT9A8PPS&hash=item4e45894000%3Ag%3Ax2kAAeSwNtZow4j-&itmprp=enc%3AAQAKAAAA8FkggFvd1GGDu0w3yXCmi1dC8gSd7qdEitPIE0ZO4d7m8p5qK46Klmv9IVutAtXJa%2Fb1mhglwMTHwKlTNF8weu8j%2FM1A2YGTv2frJ8UN4UphSypAv%2BIYj%2FO5N0z50iS7FA%2FUJlRQTPkDa6rAj%2Bp3X6rXtFo9H8VWVyS9swBQ9jW3tnbvEfr3XicB%2FyewsSqXAj4nGvBFEhgMgP7RrRNVarUc7ZvwPZgFd0RDWFCEwi0KOMm2xmAo5oBT3CKdvYNoodVDISy7kCMSVfCzG3vK2BH3dYfxtdOISefRy4bqQUTbl09%2BsIwHm4lm9wuSUs%2Fr7Q%3D%3D%7Ctkp%3ABFBM1uPqlL1m&LH_BIN=1"
]

datos_encontrados = []

# --- CONFIGURACIÓN DEL NAVEGADOR ---
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 20) 

print("Iniciando proceso de scraping multi-sitio (con soporte para eBay)...")

# --- BUCLE PRINCIPAL ---
for url in urls_a_raspar:
    print(f"\nProcesando: {url}")
    datos_extraidos = {"nombre": "Error", "precio": "Error", "imagen": "Error", "tallas": "Error"}
    
    # --- EL DIRECTOR: ELIGE QUÉ FUNCIÓN USAR ---
    if "nike.com" in url:
        datos_extraidos = scrape_nike(driver, wait, url)
    elif "amazon.com" in url:
        datos_extraidos = scrape_amazon(driver, wait, url)
    elif "ebay.com" in url:
        datos_extraidos = scrape_ebay(driver, wait, url)
    else:
        print("    -> ERROR: Sitio web no soportado.")

    # --- CÁLCULOS FINANCIEROS (LA LÓGICA ES IDÉNTICA PARA TODOS) ---
    precio_limpio = re.sub(r'[^\d.]', '', datos_extraidos['precio'])
    try:
        precio_usd = float(precio_limpio)
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

    # Guardamos todos los datos
    datos_encontrados.append({
        "Nombre del Producto": datos_extraidos['nombre'],
        "Precio Original (USD)": round(precio_usd, 2),
        "Tallas Disponibles": datos_extraidos['tallas'],
        "Costo Final por Unidad (USD)": round(costo_final_usd, 2),
        "Costo Final por Unidad (GTQ)": round(costo_final_gtq, 2),
        "Precio Sugerido Venta (GTQ)": round(precio_venta_gtq, 2),
        "Ganancia por Unidad (GTQ)": round(ganancia_gtq, 2),
        "Margen de Ganancia (%)": round(margen_ganancia, 2),
        "URL Imagen": datos_extraidos['imagen'],
        "URL Producto": url
    })

# --- LIMPIEZA Y GUARDADO ---
driver.quit()
print("\nProceso finalizado. Cerrando navegador.")

df = pd.DataFrame(datos_encontrados)
nombre_archivo_excel = "catalogo_multi_sitio_completo.xlsx"
df.to_excel(nombre_archivo_excel, index=False)

print(f"\n¡Éxito! Tu catálogo multi-sitio (Nike, Amazon, eBay) ha sido guardado en '{nombre_archivo_excel}'.")