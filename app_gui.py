#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Catálogo Generator - Aplicación de Escritorio PyQt6
Scraping profesional de Nike y Sephora
"""

import sys
import os
import threading
import json
import base64
import logging
import re
import subprocess
import time
import requests
import pickle
from datetime import datetime
from io import BytesIO
from pathlib import Path

# Configurar logging
log_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'CatalogoGenerator')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'error.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, QSpinBox,
    QFrame, QScrollArea, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QUrl
from PyQt6.QtGui import QFont, QColor, QIcon, QAction
import pandas as pd
import pyperclip
import winsound
import threading

# Importar notificador de Discord
try:
    from utils.discord_notifier import send_error_report
except ImportError:
    def send_error_report(failed_urls):
        logging.warning("Discord notifier no encontrado")

# Importar funciones de scraping
try:
    from scrapers.nike import scrape_nike, calcular_precios as nike_calcular, limpiar_precio as nike_limpiar
    from scrapers.sephora import scrape_sephora, calcular_precios as sephora_calcular, limpiar_precio as sephora_limpiar
    from src.config.settings import (
        VERSION, PALABRAS_CLAVE_CON_TALLAS, PALABRAS_CLAVE_SIN_TALLAS, 
        MARCAS_KEYWORDS, CATEGORIA_MODA, CATEGORIA_COSMETICOS
    )
    logging.info("✅ Scrapers importados correctamente")
except ImportError as e:
    logging.error(f"❌ Error al importar scrapers: {e}")
    raise

# Importar Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.support.ui import WebDriverWait
    logging.info("✅ Selenium importado correctamente")
except ImportError as e:
    logging.error(f"❌ Error al importar Selenium: {e}")
    raise

def detectar_marca(texto, url=None):
    """
    Detecta la marca basándose en:
    1. URL (si se proporciona)
    2. Texto (Nombre del producto)
    """
    texto = texto.lower()
    
    # 1. Detección por URL
    if url:
        url_lower = url.lower()
        for keyword, marca_norm in MARCAS_KEYWORDS.items():
            if keyword in url_lower:
                return marca_norm

    # 2. Detección por Nombre del Producto
    for keyword, marca_norm in MARCAS_KEYWORDS.items():
        if keyword in texto:
            return marca_norm
            
    return 'Otra'

class ScrapingThread(QThread):
    """Thread para ejecutar scraping sin bloquear la GUI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, marca, urls):
        super().__init__()
        self.marca = marca
        self.urls = urls
        self.driver = None
        self.wait = None
        self.logs = []

    def _emit_log(self, msg, level="info"):
        """Helper para emitir log, guardar historial y escribir en logging"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {msg}"
        self.logs.append(log_entry)
        self.progress.emit(msg)
        
        if level == "error":
            logging.error(msg)
        elif level == "warning":
            logging.warning(msg)
        else:
            logging.info(msg)

    def run(self):
        try:
            self._emit_log(f"🚀 Iniciando scraping de {self.marca}...")
            logging.info(f"Iniciando scraping de {self.marca} con {len(self.urls)} URLs")
            
            # Inicializar driver
            try:
                self._emit_log("⚙️ Descargando ChromeDriver...")
                logging.info("Descargando ChromeDriver")
                service = Service(ChromeDriverManager().install())
                logging.info(f"ChromeDriver instalado: {service.path}")
            except Exception as e:
                logging.error(f"Error instalando ChromeDriver: {e}")
                self.error.emit(f"Error al descargar ChromeDriver: {str(e)}")
                return
            
            try:
                options = webdriver.ChromeOptions()
                options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                self.driver = webdriver.Chrome(service=service, options=options)
                self.wait = WebDriverWait(self.driver, 20)
                logging.info("Chrome driver iniciado correctamente")
            except Exception as e:
                logging.error(f"Error iniciando Chrome driver: {e}")
                self.error.emit(f"Error al iniciar Chrome: {str(e)}")
                return
            
            datos_encontrados = []
            urls_fallidas = [] # Lista de tuplas (url, error)
            
            # Determinar scraper
            if 'nike' in self.marca.lower():
                scraper_func = scrape_nike
                calcular = nike_calcular
                logging.info("Usando scraper de Nike")
            elif 'sephora' in self.marca.lower():
                scraper_func = scrape_sephora
                calcular = sephora_calcular
                logging.info("Usando scraper de Sephora")
            else:
                error_msg = f"Marca '{self.marca}' no soportada"
                logging.error(error_msg)
                self.error.emit(error_msg)
                return

            for idx, url in enumerate(self.urls, 1):
                self._emit_log(f"[{idx}/{len(self.urls)}] Procesando: {url}")
                logging.info(f"Procesando URL {idx}: {url}")
                
                try:
                    datos_extraidos = scraper_func(self.driver, self.wait, url)
                    logging.info(f"Datos extraídos: {datos_extraidos}")
                    
                    if datos_extraidos and datos_extraidos.get('nombre') != 'Error':
                        try:
                            # Limpiar precio: extrae SOLO números y punto decimal
                            precio_str = str(datos_extraidos['precio']).strip()
                            # Eliminar símbolos de moneda y espacios
                            precio_str = precio_str.replace('US$', '').replace('$', '').replace('€', '').replace(' ', '')
                            # Mantener solo números y el primer punto
                            numeros = re.findall(r'[\d.]+', precio_str)
                            if numeros:
                                precio_usd = float(numeros[0])
                            else:
                                error_msg = f"No se pudo extraer precio de: {precio_str}"
                                self._emit_log(f"⚠️ {error_msg}", level="warning")
                                urls_fallidas.append((url, error_msg))
                                continue
                            
                            precios = calcular(precio_usd)
                            
                            # --- LÓGICA DE DETECCIÓN DE MARCA (Multi-Stage) ---
                            marca_detectada = 'Otra'
                            
                            # 1. Intentar detectar por URL
                            marca_url = detectar_marca("", url=url)
                            if marca_url != 'Otra':
                                marca_detectada = marca_url
                            else:
                                # 2. Intentar usar marca extraída por el scraper (si existe)
                                if datos_extraidos.get('marca'):
                                    marca_detectada = datos_extraidos['marca']
                                else:
                                    # 3. Intentar detectar por Nombre del Producto
                                    marca_detectada = detectar_marca(datos_extraidos['nombre'])
                            
                            row = {
                                'Marca': marca_detectada,
                                'Nombre': datos_extraidos['nombre'],
                                'Sitio': datos_extraidos.get('sitio', 'Desconocido'),
                                'Precio USD': precio_usd,
                                'Tallas': datos_extraidos.get('tallas', 'N/A'),
                                **precios
                            }
                            datos_encontrados.append(row)
                            self._emit_log(f"✅ [{marca_detectada}] {datos_extraidos['nombre']} (${precio_usd})")
                            logging.info(f"Producto agregado: {datos_extraidos['nombre']} - ${precio_usd}")
                        except (ValueError, IndexError) as e:
                            error_msg = f"Error al procesar precio de '{datos_extraidos.get('nombre', 'producto')}': {datos_extraidos['precio']}"
                            self._emit_log(f"⚠️ {error_msg}", level="error")
                            urls_fallidas.append((url, error_msg))
                    else:
                        error_msg = "No se pudieron extraer datos (Scraper retornó None/Error)"
                        self._emit_log(f"❌ {error_msg} de {url}", level="warning")
                        logging.warning(f"{error_msg} de {url}")
                        urls_fallidas.append((url, error_msg))
                        
                except Exception as e:
                    error_msg = f"Excepción: {str(e)}"
                    self._emit_log(f"❌ {error_msg}", level="error")
                    logging.error(f"Error procesando URL {url}: {e}", exc_info=True)
                    urls_fallidas.append((url, error_msg))
                    continue

            try:
                self.driver.quit()
                logging.info("Chrome driver cerrado")
            except:
                pass
            
            # Emitir finished siempre que haya terminado el loop, aunque no haya datos encontrados
            # para poder reportar los errores
            final_msg = f"✅ Extracción completada: {len(datos_encontrados)} productos, {len(urls_fallidas)} fallidos"
            self._emit_log(final_msg)
            
            # Preparar snippet de log (últimas 30 líneas)
            log_snippet = "\n".join(self.logs[-30:])
            
            self.finished.emit({
                'success': True,
                'data': datos_encontrados,
                'count': len(datos_encontrados),
                'failed': urls_fallidas,
                'log_snippet': log_snippet
            })
                
        except Exception as e:
            error_msg = f"Error general: {str(e)}"
            logging.error(error_msg, exc_info=True)
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.error.emit(error_msg)


class ClipboardMonitor(QThread):
    """Monitorea el portapapeles en busca de URLs de productos"""
    url_detected = pyqtSignal(str)  # Solo envía la URL

    def __init__(self):
        super().__init__()
        self.running = True
        self.last_text = ""

    def run(self):
        try:
            import pyperclip
            import winsound
        except ImportError as e:
            logging.error(f"Error importando dependencias de ClipboardMonitor: {e}")
            return

        # Inicializar con el contenido actual para ignorar lo que ya estaba copiado
        try:
            self.last_text = pyperclip.paste().strip()
        except:
            self.last_text = ""
            
        self.running = True  # Asegurar que el flag esté en True al iniciar

        while self.running:
            try:
                text = pyperclip.paste().strip()
                if text and text != self.last_text:
                    self.last_text = text
                    if text.startswith('http'):
                        # Simple: Detecta URL y emite señal
                        try:
                            winsound.Beep(1000, 100) # Duración reducida a 100ms
                        except:
                            pass
                        self.url_detected.emit(text)
            except Exception as e:
                logging.error(f"Error en ClipboardMonitor: {e}")
            
            time.sleep(1.0)

    def stop(self):
        self.running = False
        self.wait()


class NikeTab(QWidget):
    """Tab para scraping de Nike"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.scraping_thread = None

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("🔍 Scraping Moda (Nike, Adidas, etc.)")
        titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(titulo)
        
        # Input de URLs
        layout.addWidget(QLabel("URLs de Nike (una por línea):"))
        self.urls_input = QTextEdit()
        self.urls_input.setPlaceholderText("https://www.nike.com/t/...\nhttps://www.nike.com/t/...")
        layout.addWidget(self.urls_input)
        
        # Botón de scraping
        self.scrape_btn = QPushButton("🚀 Scraping Nike")
        self.scrape_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #333333; }
        """)
        self.scrape_btn.clicked.connect(self.iniciar_scraping)
        layout.addWidget(self.scrape_btn)
        
        # Log
        layout.addWidget(QLabel("Log:"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(150)
        layout.addWidget(self.log)
        
        # Tabla de resultados
        layout.addWidget(QLabel("Resultados:"))
        self.resultados_table = QTableWidget()
        self.resultados_table.setColumnCount(4)
        self.resultados_table.setHorizontalHeaderLabels(['Marca', 'Producto', 'Sitio', 'Precio USD'])
        self.resultados_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.resultados_table.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        layout.addWidget(self.resultados_table)
        
        # Botón descargar
        self.download_btn = QPushButton("💾 Descargar Excel")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.descargar_excel)
        layout.addWidget(self.download_btn)
        
        self.setLayout(layout)
        self.datos_scrapeados = []

    def mostrar_menu_contextual(self, position):
        menu = QMenu()
        
        eliminar_action = QAction("❌ Eliminar", self)
        eliminar_action.triggered.connect(self.eliminar_fila)
        menu.addAction(eliminar_action)
        
        mover_action = QAction("➡️ Mover a Cosméticos", self)
        mover_action.triggered.connect(self.mover_fila)
        menu.addAction(mover_action)
        
        menu.exec(self.resultados_table.viewport().mapToGlobal(position))

    def eliminar_fila(self):
        row = self.resultados_table.currentRow()
        if row >= 0:
            del self.datos_scrapeados[row]
            self.mostrar_resultados()

    def mover_fila(self):
        row = self.resultados_table.currentRow()
        if row >= 0:
            producto = self.datos_scrapeados.pop(row)
            self.mostrar_resultados()
            if self.window() and hasattr(self.window(), 'mover_producto'):
                self.window().mover_producto(producto, 'Cosméticos')

    def process_url(self, url):
        """Procesa una URL externa (Clipboard Monitor)"""
        current_text = self.urls_input.toPlainText()
        if current_text:
            self.urls_input.append(url)
        else:
            self.urls_input.setText(url)
            
        self.log.append(f"🤖 Link detectado y agregado: {url}")
        
        # Auto-scraping (opcional)
        # self.iniciar_scraping()

    def append_result(self, result):
        if result['success']:
            new_data = result['data']
            
            # Filtrar y Mover Automáticamente
            productos_para_aqui = []
            for producto in new_data:
                marca = producto.get('Marca', 'Otra')
                if marca in CATEGORIA_COSMETICOS:
                    # Mover a SephoraTab
                    if self.window() and hasattr(self.window(), 'mover_producto'):
                        self.window().mover_producto(producto, 'Cosméticos')
                else:
                    productos_para_aqui.append(producto)
            
            self.datos_scrapeados.extend(productos_para_aqui)
            self.mostrar_resultados()
            self.download_btn.setEnabled(True)
            self.log.append(f"✅ Auto-captura: {len(productos_para_aqui)} productos agregados (Movidos: {len(new_data) - len(productos_para_aqui)})")

    def iniciar_scraping(self):
        urls = self.urls_input.toPlainText().strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        
        if not urls:
            QMessageBox.warning(self, "Error", "Ingresa al menos una URL")
            return
        
        self.scrape_btn.setEnabled(False)
        self.log.clear()
        # No limpiar la tabla para permitir "Append"
        # self.resultados_table.setRowCount(0) 
        
        self.scraping_thread = ScrapingThread("Nike", urls)
        self.scraping_thread.progress.connect(self.agregar_log)
        self.scraping_thread.finished.connect(self.scraping_completado)
        self.scraping_thread.error.connect(self.mostrar_error)
        self.scraping_thread.start()

    def agregar_log(self, mensaje):
        self.log.append(mensaje)

    def scraping_completado(self, resultado):
        if resultado['success']:
            nuevos_datos = resultado['data']
            fallidos = resultado.get('failed', [])
            agregados = 0
            duplicados = 0
            
            # Nombres existentes para verificar duplicados
            nombres_existentes = {p.get('Nombre') for p in self.datos_scrapeados}
            
            for producto in nuevos_datos:
                if producto.get('Nombre') not in nombres_existentes:
                    self.datos_scrapeados.append(producto)
                    nombres_existentes.add(producto.get('Nombre'))
                    agregados += 1
                else:
                    duplicados += 1
            
            self.mostrar_resultados()
            self.download_btn.setEnabled(True)
            
            msg = "✅ Proceso completado."
            if agregados > 0:
                msg += f"\nNuevos: {agregados}"
            if duplicados > 0:
                msg += f"\n⚠️ Hay {duplicados} duplicados (omitidos)."
            
            if agregados == 0 and duplicados == 0 and not fallidos:
                 msg += "\nNo se encontraron datos nuevos."

            if fallidos:
                msg += f"\n❌ {len(fallidos)} Errores (Reportados a Discord)"
                log_snippet = resultado.get('log_snippet', '')
                # Enviar reporte a Discord en hilo separado para no bloquear GUI
                threading.Thread(target=send_error_report, args=(fallidos, log_snippet), daemon=True).start()

            self.log.append(msg)
            QMessageBox.information(self, "Reporte de Scraping", msg)
            
        self.scrape_btn.setEnabled(True)

    def mostrar_resultados(self):
        self.resultados_table.setRowCount(len(self.datos_scrapeados))
        for row, producto in enumerate(self.datos_scrapeados):
            # Color coding
            marca = producto.get('Marca', 'Otra')
            color = None
            if marca == 'Otra':
                color = QColor(255, 200, 150) # Naranja claro
            elif marca not in CATEGORIA_MODA:
                color = QColor(255, 255, 200) # Amarillo claro
            
            # Items
            item_marca = QTableWidgetItem(marca)
            item_nombre = QTableWidgetItem(producto.get('Nombre', ''))
            item_sitio = QTableWidgetItem(producto.get('Sitio', ''))
            item_precio = QTableWidgetItem(str(producto.get('Precio USD', '')))
            
            if color:
                item_marca.setBackground(color)
                item_nombre.setBackground(color)
                item_sitio.setBackground(color)
                item_precio.setBackground(color)

            self.resultados_table.setItem(row, 0, item_marca)
            self.resultados_table.setItem(row, 1, item_nombre)
            self.resultados_table.setItem(row, 2, item_sitio)
            self.resultados_table.setItem(row, 3, item_precio)

    def mostrar_error(self, error):
        self.log.append(f"❌ {error}")
        self.scrape_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", error)

    def descargar_excel(self):
        if not self.datos_scrapeados:
            QMessageBox.warning(self, "Error", "No hay datos para descargar")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Excel", "", "Excel Files (*.xlsx)"
        )
        
        if path:
            try:
                df = pd.DataFrame(self.datos_scrapeados)
                df.to_excel(path, index=False)
                QMessageBox.information(self, "Éxito", f"Archivo guardado en:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error guardando archivo:\n{e}")


class SephoraTab(QWidget):
    """Tab para scraping de Sephora"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.scraping_thread = None

    def init_ui(self):
        layout = QVBoxLayout()
        
        titulo = QLabel("🔍 Scraping Cosméticos (Sephora, etc.)")
        titulo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(titulo)
        
        layout.addWidget(QLabel("URLs de Sephora (una por línea):"))
        self.urls_input = QTextEdit()
        self.urls_input.setPlaceholderText("https://www.sephora.com/...\nhttps://www.sephora.com/...")
        layout.addWidget(self.urls_input)
        
        self.scrape_btn = QPushButton("🚀 Scraping Sephora")
        self.scrape_btn.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #333333; }
        """)
        self.scrape_btn.clicked.connect(self.iniciar_scraping)
        layout.addWidget(self.scrape_btn)
        
        layout.addWidget(QLabel("Log:"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(150)
        layout.addWidget(self.log)

        # Tabla de resultados
        layout.addWidget(QLabel("Resultados:"))
        self.resultados_table = QTableWidget()
        self.resultados_table.setColumnCount(4)
        self.resultados_table.setHorizontalHeaderLabels(['Marca', 'Producto', 'Sitio', 'Precio USD'])
        self.resultados_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.resultados_table.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        layout.addWidget(self.resultados_table)
        
        # Botón descargar
        self.download_btn = QPushButton("💾 Descargar Excel")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.descargar_excel)
        layout.addWidget(self.download_btn)
        
        self.setLayout(layout)
        self.datos_scrapeados = []

    def mostrar_menu_contextual(self, position):
        menu = QMenu()
        
        eliminar_action = QAction("❌ Eliminar", self)
        eliminar_action.triggered.connect(self.eliminar_fila)
        menu.addAction(eliminar_action)
        
        mover_action = QAction("➡️ Mover a Moda", self)
        mover_action.triggered.connect(self.mover_fila)
        menu.addAction(mover_action)
        
        menu.exec(self.resultados_table.viewport().mapToGlobal(position))

    def eliminar_fila(self):
        row = self.resultados_table.currentRow()
        if row >= 0:
            del self.datos_scrapeados[row]
            self.mostrar_resultados()

    def mover_fila(self):
        row = self.resultados_table.currentRow()
        if row >= 0:
            producto = self.datos_scrapeados.pop(row)
            self.mostrar_resultados()
            if self.window() and hasattr(self.window(), 'mover_producto'):
                self.window().mover_producto(producto, 'Moda')

    def process_url(self, url):
        """Procesa una URL externa (Clipboard Monitor)"""
        current_text = self.urls_input.toPlainText()
        if current_text:
            self.urls_input.append(url)
        else:
            self.urls_input.setText(url)
            
        self.log.append(f"🤖 Link detectado y agregado: {url}")

    def append_result(self, result):
        if result['success']:
            new_data = result['data']
            
            # Filtrar y Mover Automáticamente
            productos_para_aqui = []
            for producto in new_data:
                marca = producto.get('Marca', 'Otra')
                if marca in CATEGORIA_MODA:
                    # Mover a NikeTab
                    if self.window() and hasattr(self.window(), 'mover_producto'):
                        self.window().mover_producto(producto, 'Moda')
                else:
                    productos_para_aqui.append(producto)

            self.datos_scrapeados.extend(productos_para_aqui)
            self.mostrar_resultados()
            self.download_btn.setEnabled(True)
            self.log.append(f"✅ Auto-captura: {len(productos_para_aqui)} productos agregados (Movidos: {len(new_data) - len(productos_para_aqui)})")

    def iniciar_scraping(self):
        urls = self.urls_input.toPlainText().strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        
        if not urls:
            QMessageBox.warning(self, "Error", "Ingresa al menos una URL")
            return
        
        self.scrape_btn.setEnabled(False)
        self.log.clear()
        # No limpiar la tabla para permitir "Append"
        # self.resultados_table.setRowCount(0)
        
        self.scraping_thread = ScrapingThread("Sephora", urls)
        self.scraping_thread.progress.connect(self.agregar_log)
        self.scraping_thread.finished.connect(self.scraping_completado)
        self.scraping_thread.error.connect(self.mostrar_error)
        self.scraping_thread.start()

    def agregar_log(self, mensaje):
        self.log.append(mensaje)

    def scraping_completado(self, resultado):
        if resultado['success']:
            nuevos_datos = resultado['data']
            fallidos = resultado.get('failed', [])
            agregados = 0
            duplicados = 0
            
            # Nombres existentes para verificar duplicados
            nombres_existentes = {p.get('Nombre') for p in self.datos_scrapeados}
            
            for producto in nuevos_datos:
                if producto.get('Nombre') not in nombres_existentes:
                    self.datos_scrapeados.append(producto)
                    nombres_existentes.add(producto.get('Nombre'))
                    agregados += 1
                else:
                    duplicados += 1
            
            self.mostrar_resultados()
            self.download_btn.setEnabled(True)
            
            msg = "✅ Proceso completado."
            if agregados > 0:
                msg += f"\nNuevos: {agregados}"
            if duplicados > 0:
                msg += f"\n⚠️ Hay {duplicados} duplicados (omitidos)."
            
            if agregados == 0 and duplicados == 0 and not fallidos:
                 msg += "\nNo se encontraron datos nuevos."

            if fallidos:
                msg += f"\n❌ {len(fallidos)} Errores (Reportados a Discord)"
                log_snippet = resultado.get('log_snippet', '')
                # Enviar reporte a Discord en hilo separado para no bloquear GUI
                threading.Thread(target=send_error_report, args=(fallidos, log_snippet), daemon=True).start()

            self.log.append(msg)
            QMessageBox.information(self, "Reporte de Scraping", msg)
            
        self.scrape_btn.setEnabled(True)

    def mostrar_resultados(self):
        self.resultados_table.setRowCount(len(self.datos_scrapeados))
        for row, producto in enumerate(self.datos_scrapeados):
            self.resultados_table.setItem(row, 0, QTableWidgetItem(producto.get('Marca', 'Otra')))
            self.resultados_table.setItem(row, 1, QTableWidgetItem(producto.get('Nombre', '')))
            self.resultados_table.setItem(row, 2, QTableWidgetItem(producto.get('Sitio', '')))
            self.resultados_table.setItem(row, 3, QTableWidgetItem(str(producto.get('Precio USD', ''))))

    def mostrar_error(self, error):
        self.log.append(f"❌ {error}")
        self.scrape_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", error)

    def descargar_excel(self):
        if not self.datos_scrapeados:
            QMessageBox.warning(self, "Error", "No hay datos para descargar")
            return
        
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Excel", "", "Excel Files (*.xlsx)"
        )
        
        if path:
            try:
                df = pd.DataFrame(self.datos_scrapeados)
                
                # Eliminar columna 'Tallas' si existe (solo para Cosméticos)
                if 'Tallas' in df.columns:
                    df = df.drop(columns=['Tallas'])
                    
                df.to_excel(path, index=False)
                QMessageBox.information(self, "Éxito", f"Archivo guardado en:\n{path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error guardando archivo:\n{e}")


class UpdaterWorker(QThread):
    """Worker thread para descargar actualizaciones sin bloquear la GUI"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # (success, message)
    
    def run(self):
        try:
            self.progress.emit("🔍 Verificando actualizaciones...")
            
            # 1. Leer versión local
            # Si está congelado (exe), usar sys._MEIPASS
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
                
            # En desarrollo, el archivo está en src/config/settings.py
            # Pero aquí ya importamos VERSION, así que usamos esa
            local_version = VERSION
            
            # 2. Consultar GitHub API
            # Reemplaza con tu repo: 'usuario/repo'
            repo = "JoshuaMzV/Scrapping-Web" 
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            
            headers = {"Accept": "application/vnd.github.v3+json"}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            # GitHub Actions uses 'latest' as tag, but puts the version in 'name' (e.g. "v3.0.12")
            remote_version_raw = release_data.get('name', '')
            if not remote_version_raw or 'latest' in remote_version_raw.lower():
                 remote_version_raw = release_data.get('tag_name', '')
            
            remote_version = remote_version_raw.replace('v', '').strip()
            local_version = str(local_version).replace('v', '').strip()
            
            # Comparación semántica de versiones
            def parse_version(v):
                return [int(x) for x in v.split('.')] if v else [0]

            logging.info(f"Verificando actualizaciones: Local='{local_version}' vs Remote='{remote_version}'")
            
            try:
                remote_parts = parse_version(remote_version)
                local_parts = parse_version(local_version)
                
                # Si remote <= local, no hay update
                if remote_parts <= local_parts:
                     self.finished.emit(False, f"✅ Ya tienes la versión más reciente: {local_version}")
                     return
            except Exception as e:
                logging.error(f"Error comparando versiones: {e}")
                # Fallback a string comparison si falla el parseo
                if remote_version <= local_version:
                     self.finished.emit(False, f"✅ Ya tienes la versión más reciente: {local_version}")
                     return

            self.progress.emit(f"📥 Nueva versión disponible: {remote_version}")
            
            # 3. Descargar nuevo .exe
            assets = release_data.get('assets', [])
            if not assets:
                self.finished.emit(False, "❌ No se encontró archivo .exe en la release")
                return
            
            exe_asset = assets[0]
            download_url = exe_asset['browser_download_url']
            
            self.progress.emit("⬇️ Descargando nuevo ejecutable...")
            
            exe_response = requests.get(download_url, stream=True, timeout=60)
            exe_response.raise_for_status()
            
            # Guardar como temporal
            # Usamos el directorio del ejecutable actual para guardar el temporal
            if getattr(sys, 'frozen', False):
                current_dir = os.path.dirname(sys.executable)
            else:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                
            temp_exe = os.path.join(current_dir, "update_new.exe")
            
            with open(temp_exe, 'wb') as f:
                for chunk in exe_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            self.progress.emit("✅ Descarga completada")
            
            # 4. Crear script BAT para actualizar
            current_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.join(current_dir, "app_gui.py")
            old_exe_name = "CatalogoGenerator_old.exe"
            
            bat_script = f"""@echo off
timeout /t 2 /nobreak > NUL
set OLD_EXE="{current_exe}"
set NEW_EXE="{temp_exe}"
set BACKUP_EXE="{os.path.join(current_dir, old_exe_name)}"

if exist %OLD_EXE% (
    del %BACKUP_EXE% 2>NUL
    move /Y %OLD_EXE% %BACKUP_EXE%
)

move /Y %NEW_EXE% %OLD_EXE%

if exist %OLD_EXE% (
    start "" %OLD_EXE%
)

timeout /t 1 /nobreak > NUL
del "%~f0"
"""
            
            bat_file = os.path.join(current_dir, "update.bat")
            with open(bat_file, 'w') as f:
                f.write(bat_script)
            
            self.progress.emit("🔄 Preparando reinicio...")
            self.finished.emit(True, "✅ Actualización descargada. Reiniciando en 3 segundos...")
            
            # 5. Ejecutar BAT y terminar esta aplicación
            time.sleep(3)
            subprocess.Popen(bat_file, shell=True)
            sys.exit()
            
        except requests.exceptions.Timeout:
            self.finished.emit(False, "⏱️ Timeout conectando con GitHub")
        except requests.exceptions.ConnectionError:
            self.finished.emit(False, "❌ Error de conexión con GitHub")
        except Exception as e:
            logging.error(f"Error actualización: {e}", exc_info=True)
            self.finished.emit(False, f"❌ Error: {str(e)}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Catálogo Generator v{VERSION}")
        self.setGeometry(100, 100, 1000, 700)
        
        self.current_session_path = None  # Para "Guardar" directo
        
        # Tema oscuro
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane { border: 1px solid #444; }
            QTabBar::tab { background-color: #333; padding: 8px 20px; color: white; }
            QTabBar::tab:selected { background-color: #555; }
            QLabel { color: #ffffff; }
            QTextEdit { background-color: #2d2d2d; color: #00ff00; border: 1px solid #444; }
            QTableWidget { background-color: #2d2d2d; color: #ffffff; }
            QTableWidget::item { padding: 5px; }
            QPushButton { font-weight: bold; }
        """)
        
        self.create_menu_bar()  # Crear menú superior
        
        # Widget central con tabs
        self.tabs = QTabWidget()
        
        self.nike_tab = NikeTab()
        self.sephora_tab = SephoraTab()
        
        self.tabs.addTab(self.nike_tab, "👟 Moda")
        self.tabs.addTab(self.sephora_tab, "💄 Cosméticos")
        
        self.setCentralWidget(self.tabs)
        
        # Toolbar para Auto-Capture
        toolbar = self.addToolBar("Herramientas")
        self.auto_capture_btn = QPushButton("🔴 Auto-Capture: OFF")
        self.auto_capture_btn.setCheckable(True)
        self.auto_capture_btn.clicked.connect(self.toggle_auto_capture)
        self.auto_capture_btn.setStyleSheet("color: red; font-weight: bold;")
        toolbar.addWidget(self.auto_capture_btn)
        
        # Clipboard Monitor
        self.clipboard_monitor = ClipboardMonitor()
        self.clipboard_monitor.url_detected.connect(self.on_clipboard_url_detected)
        
        self.updater_worker = None

        # Status bar con botón de actualización
        status_bar = self.statusBar()
        status_bar.showMessage(f"Catálogo Generator v{VERSION} - Listo")
        
        update_btn = QPushButton("🔄 Buscar Actualización")
        update_btn.setMaximumWidth(200)
        update_btn.clicked.connect(self.check_for_updates)
        status_bar.addPermanentWidget(update_btn)
        
        # Iniciar worker de actualización
        # self.check_for_updates() # Desactivado temporalmente para no molestar en dev
        
        # Verificar consentimiento de privacidad (Primera ejecución)
        self.check_privacy_consent()
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # Menú Archivo
        file_menu = menu_bar.addMenu("Archivo")
        
        # Acciones
        open_action = QAction("📂 Abrir Sesión...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_session)
        file_menu.addAction(open_action)
        
        save_action = QAction("💾 Guardar Sesión", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_session)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("📝 Guardar Sesión Como...", self)
        save_as_action.triggered.connect(self.save_session_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def save_session(self):
        """Guarda la sesión actual. Si no hay archivo, pide uno."""
        if self.current_session_path:
            self._save_to_file(self.current_session_path)
        else:
            self.save_session_as()

    def save_session_as(self):
        """Pide ubicación y guarda la sesión."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Sesión", "", "Catalogo Session (*.cgs)"
        )
        if path:
            self.current_session_path = path
            self._save_to_file(path)

    def _save_to_file(self, path):
        """Lógica interna de guardado"""
        try:
            session_data = {
                'version': VERSION,
                'nike_data': self.nike_tab.datos_scrapeados,
                'sephora_data': self.sephora_tab.datos_scrapeados,
                'timestamp': datetime.now().isoformat()
            }
            with open(path, 'wb') as f:
                pickle.dump(session_data, f)
            
            self.setWindowTitle(f"Catálogo Generator v{VERSION} - {os.path.basename(path)}")
            self.statusBar().showMessage(f"✅ Sesión guardada: {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar sesión:\n{e}")

    def load_session(self):
        """Carga una sesión desde archivo"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Sesión", "", "Catalogo Session (*.cgs)"
        )
        if path:
            try:
                with open(path, 'rb') as f:
                    session_data = pickle.load(f)
                
                # Cargar datos
                self.nike_tab.datos_scrapeados = session_data.get('nike_data', [])
                self.sephora_tab.datos_scrapeados = session_data.get('sephora_data', [])
                
                # Refrescar tablas
                self.nike_tab.mostrar_resultados()
                self.sephora_tab.mostrar_resultados()
                
                # Habilitar botones de descarga si hay datos
                self.nike_tab.download_btn.setEnabled(bool(self.nike_tab.datos_scrapeados))
                self.sephora_tab.download_btn.setEnabled(bool(self.sephora_tab.datos_scrapeados))
                
                self.current_session_path = path
                self.setWindowTitle(f"Catálogo Generator v{VERSION} - {os.path.basename(path)}")
                self.statusBar().showMessage(f"📂 Sesión cargada: {os.path.basename(path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al cargar sesión:\n{e}")

    def mover_producto(self, producto, destino):
        """Mueve un producto de un tab a otro"""
        if destino == 'Cosméticos':
            self.sephora_tab.datos_scrapeados.append(producto)
            self.sephora_tab.mostrar_resultados()
            self.sephora_tab.download_btn.setEnabled(True)
            # Switch focus to target tab (optional, maybe annoying if auto-moving)
            # self.tabs.setCurrentWidget(self.sephora_tab)
            logging.info(f"Producto movido a Cosméticos: {producto.get('Nombre')}")
            
        elif destino == 'Moda':
            self.nike_tab.datos_scrapeados.append(producto)
            self.nike_tab.mostrar_resultados()
            self.nike_tab.download_btn.setEnabled(True)
            logging.info(f"Producto movido a Moda: {producto.get('Nombre')}")

    def check_for_updates(self):
        """Inicia el proceso de verificación de actualizaciones"""
        if self.updater_worker and self.updater_worker.isRunning():
            QMessageBox.information(self, "Info", "Ya hay una actualización en progreso...")
            return
        
        self.updater_worker = UpdaterWorker()
        self.updater_worker.progress.connect(lambda msg: self.statusBar().showMessage(msg))
        self.updater_worker.finished.connect(self.on_update_finished)
        self.updater_worker.start()
    
    def on_update_finished(self, success, message):
        """Manejador cuando termina la verificación de actualizaciones"""
        self.statusBar().showMessage(f"Catálogo Generator v{VERSION} - Listo")
        if success:
            QMessageBox.information(self, "Actualización", message)
        else:
            QMessageBox.information(self, "Verificación de Actualización", message)

    def toggle_auto_capture(self, checked):
        if checked:
            self.auto_capture_btn.setText("🟢 Auto-Capture: ON")
            self.auto_capture_btn.setStyleSheet("color: #00ff00; font-weight: bold;")
            self.clipboard_monitor.start()
            self.statusBar().showMessage("Monitor de portapapeles activado")
        else:
            self.auto_capture_btn.setText("🔴 Auto-Capture: OFF")
            self.auto_capture_btn.setStyleSheet("color: red; font-weight: bold;")
            self.clipboard_monitor.stop()
            self.statusBar().showMessage("Monitor de portapapeles desactivado")

    def on_clipboard_url_detected(self, url):
        # Obtener el índice del tab actual
        current_index = self.tabs.currentIndex()
        
        if current_index == 0:
            self.nike_tab.process_url(url)
            self.statusBar().showMessage(f"🔗 Link agregado a Moda: {url}")
        elif current_index == 1:
            self.sephora_tab.process_url(url)
            self.statusBar().showMessage(f"🔗 Link agregado a Cosméticos: {url}")

    def check_privacy_consent(self):
        """Verifica si el usuario ha aceptado el consentimiento de privacidad."""
        consent_file = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'CatalogoGenerator', 'privacy_consent.json')
        
        if not os.path.exists(consent_file):
            # Mostrar diálogo
            msg = QMessageBox(self)
            msg.setWindowTitle("Consentimiento de Privacidad y Uso")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setText("Mejora Continua y Privacidad")
            
            disclaimer = (
                "Para mejorar continuamente la calidad de 'Catálogo Generator', esta aplicación "
                "recopila información técnica anónima en caso de errores.\n\n"
                "Datos recopilados:\n"
                "- Información del Sistema (SO, Versión de Python, Nombre de PC).\n"
                "- Logs de errores técnicos (Snippets de código).\n"
                "- Estado de la aplicación al momento del fallo.\n\n"
                "Esta información se utiliza ÚNICAMENTE para depuración y mantenimiento.\n"
                "Al continuar, aceptas el envío de estos reportes automáticos."
            )
            msg.setInformativeText(disclaimer)
            
            # Botón único de aceptar
            accept_btn = msg.addButton("Aceptar y Continuar", QMessageBox.ButtonRole.AcceptRole)
            # Evitar cerrar con X o Escape sin aceptar explícitamente (aunque exec() bloquea)
            msg.setEscapeButton(None) 
            
            msg.exec()
            
            if msg.clickedButton() == accept_btn:
                # Guardar consentimiento
                try:
                    with open(consent_file, 'w') as f:
                        json.dump({"accepted": True, "date": str(datetime.now())}, f)
                    logging.info("Consentimiento de privacidad aceptado y guardado.")
                except Exception as e:
                    logging.error(f"Error guardando consentimiento: {e}")
            else:
                # Si de alguna forma cierran sin aceptar (Alt+F4), salir
                sys.exit(0)


def handle_exception(exc_type, exc_value, exc_traceback):
    """Manejador global de excepciones no capturadas"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    # Enviar reporte crítico a Discord
    try:
        import traceback
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        log_snippet = "".join(tb_lines)
        send_error_report([], log_snippet=log_snippet, is_critical=True)
    except:
        pass

    # Mostrar diálogo de error si hay GUI
    try:
        from PyQt6.QtWidgets import QMessageBox
        msg = f"Error Crítico:\n{exc_value}"
        # No podemos usar self aquí, así que creamos un box simple
        # Ojo: esto puede fallar si la app ya murió, pero intentamos
        pass 
    except:
        pass

    sys.__excepthook__(exc_type, exc_value, exc_traceback)

def main():
    # Registrar hook de excepciones
    sys.excepthook = handle_exception

    logging.info("=" * 80)
    logging.info(f"🚀 Iniciando Catálogo Generator v{VERSION}")
    logging.info(f"📁 Log file: {log_file}")
    logging.info("=" * 80)
    
    try:
        app = QApplication(sys.argv)
        logging.info("✅ QApplication creado")
        
        window = MainWindow()
        logging.info("✅ MainWindow creado")
        
        window.show()
        logging.info("✅ Ventana mostrada")
        
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"❌ Error en main(): {e}", exc_info=True)
        # Intentar reportar si main falla
        try:
            send_error_report([], log_snippet=str(e), is_critical=True)
        except:
            pass
        raise


if __name__ == '__main__':
    main()
