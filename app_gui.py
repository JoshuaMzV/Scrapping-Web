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
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QUrl
from PyQt6.QtGui import QFont, QColor, QIcon
import pandas as pd

# Importar funciones de scraping
try:
    from scrapers.nike import scrape_nike, calcular_precios as nike_calcular, limpiar_precio as nike_limpiar
    from scrapers.sephora import scrape_sephora, calcular_precios as sephora_calcular, limpiar_precio as sephora_limpiar
    from src.config.settings import VERSION
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

    def run(self):
        try:
            self.progress.emit(f"🚀 Iniciando scraping de {self.marca}...")
            logging.info(f"Iniciando scraping de {self.marca} con {len(self.urls)} URLs")
            
            # Inicializar driver
            try:
                self.progress.emit("⚙️ Descargando ChromeDriver...")
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
                self.progress.emit(f"[{idx}/{len(self.urls)}] Procesando: {url}")
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
                                self.progress.emit(f"⚠️ No se pudo extraer precio de: {precio_str}")
                                continue
                            
                            precios = calcular(precio_usd)
                            
                            row = {
                                'Nombre': datos_extraidos['nombre'],
                                'Sitio': datos_extraidos.get('sitio', 'Desconocido'),
                                'Precio USD': precio_usd,
                                'Tallas': datos_extraidos.get('tallas', 'N/A'),
                                **precios
                            }
                            datos_encontrados.append(row)
                            self.progress.emit(f"✅ {datos_extraidos['nombre']} (${precio_usd})")
                            logging.info(f"Producto agregado: {datos_extraidos['nombre']} - ${precio_usd}")
                        except (ValueError, IndexError) as e:
                            error_msg = f"Error al procesar precio de '{datos_extraidos.get('nombre', 'producto')}': {datos_extraidos['precio']}"
                            logging.error(error_msg)
                            self.progress.emit(f"⚠️ {error_msg}")
                    else:
                        self.progress.emit(f"❌ Error extrayendo datos de {url}")
                        logging.warning(f"No se extrajeron datos de {url}")
                        
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    self.progress.emit(error_msg)
                    logging.error(f"Error procesando URL {url}: {e}", exc_info=True)
                    continue

            try:
                self.driver.quit()
                logging.info("Chrome driver cerrado")
            except:
                pass
            
            if datos_encontrados:
                self.progress.emit(f"✅ Extracción completada: {len(datos_encontrados)} productos")
                logging.info(f"Extracción completada: {len(datos_encontrados)} productos")
                self.finished.emit({
                    'success': True,
                    'data': datos_encontrados,
                    'count': len(datos_encontrados)
                })
            else:
                self.error.emit("No se extrajeron datos")
                logging.warning("No se extrajeron datos")
                
        except Exception as e:
            error_msg = f"Error general: {str(e)}"
            logging.error(error_msg, exc_info=True)
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
            self.error.emit(error_msg)


class NikeTab(QWidget):
    """Tab para scraping de Nike"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.scraping_thread = None

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Título
        titulo = QLabel("🔍 Scraping Nike")
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
                background-color: #FF6600;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #E55A00; }
        """)
        self.scrape_btn.clicked.connect(self.iniciar_scraping)
        layout.addWidget(self.scrape_btn)
        
        # Progress
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Log
        layout.addWidget(QLabel("Log:"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(150)
        layout.addWidget(self.log)
        
        # Tabla de resultados
        layout.addWidget(QLabel("Resultados:"))
        self.resultados_table = QTableWidget()
        self.resultados_table.setColumnCount(3)
        self.resultados_table.setHorizontalHeaderLabels(['Producto', 'Sitio', 'Precio USD'])
        layout.addWidget(self.resultados_table)
        
        # Botón descargar
        self.download_btn = QPushButton("💾 Descargar Excel")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.descargar_excel)
        layout.addWidget(self.download_btn)
        
        self.setLayout(layout)
        self.datos_scrapeados = []

    def iniciar_scraping(self):
        urls = self.urls_input.toPlainText().strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        
        if not urls:
            QMessageBox.warning(self, "Error", "Ingresa al menos una URL")
            return
        
        self.scrape_btn.setEnabled(False)
        self.log.clear()
        self.resultados_table.setRowCount(0)
        
        self.scraping_thread = ScrapingThread("Nike", urls)
        self.scraping_thread.progress.connect(self.agregar_log)
        self.scraping_thread.finished.connect(self.scraping_completado)
        self.scraping_thread.error.connect(self.mostrar_error)
        self.scraping_thread.start()

    def agregar_log(self, mensaje):
        self.log.append(mensaje)

    def scraping_completado(self, resultado):
        if resultado['success']:
            self.datos_scrapeados = resultado['data']
            self.mostrar_resultados()
            self.download_btn.setEnabled(True)
            QMessageBox.information(self, "Éxito", f"Se extrajeron {resultado['count']} productos")
        self.scrape_btn.setEnabled(True)

    def mostrar_resultados(self):
        self.resultados_table.setRowCount(len(self.datos_scrapeados))
        for row, producto in enumerate(self.datos_scrapeados):
            self.resultados_table.setItem(row, 0, QTableWidgetItem(producto.get('Nombre', '')))
            self.resultados_table.setItem(row, 1, QTableWidgetItem(producto.get('Sitio', '')))
            self.resultados_table.setItem(row, 2, QTableWidgetItem(str(producto.get('Precio USD', ''))))

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
        
        titulo = QLabel("🔍 Scraping Sephora")
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
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        layout.addWidget(QLabel("Log:"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(150)
        layout.addWidget(self.log)
        
        layout.addWidget(QLabel("Resultados:"))
        self.resultados_table = QTableWidget()
        self.resultados_table.setColumnCount(3)
        self.resultados_table.setHorizontalHeaderLabels(['Producto', 'Sitio', 'Precio USD'])
        layout.addWidget(self.resultados_table)
        
        self.download_btn = QPushButton("💾 Descargar Excel")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.descargar_excel)
        layout.addWidget(self.download_btn)
        
        self.setLayout(layout)
        self.datos_scrapeados = []

    def iniciar_scraping(self):
        urls = self.urls_input.toPlainText().strip().split('\n')
        urls = [u.strip() for u in urls if u.strip()]
        
        if not urls:
            QMessageBox.warning(self, "Error", "Ingresa al menos una URL")
            return
        
        self.scrape_btn.setEnabled(False)
        self.log.clear()
        self.resultados_table.setRowCount(0)
        
        self.scraping_thread = ScrapingThread("Sephora", urls)
        self.scraping_thread.progress.connect(self.agregar_log)
        self.scraping_thread.finished.connect(self.scraping_completado)
        self.scraping_thread.error.connect(self.mostrar_error)
        self.scraping_thread.start()

    def agregar_log(self, mensaje):
        self.log.append(mensaje)

    def scraping_completado(self, resultado):
        if resultado['success']:
            self.datos_scrapeados = resultado['data']
            self.mostrar_resultados()
            self.download_btn.setEnabled(True)
            QMessageBox.information(self, "Éxito", f"Se extrajeron {resultado['count']} productos")
        self.scrape_btn.setEnabled(True)

    def mostrar_resultados(self):
        self.resultados_table.setRowCount(len(self.datos_scrapeados))
        for row, producto in enumerate(self.datos_scrapeados):
            self.resultados_table.setItem(row, 0, QTableWidgetItem(producto.get('Nombre', '')))
            self.resultados_table.setItem(row, 1, QTableWidgetItem(producto.get('Sitio', '')))
            self.resultados_table.setItem(row, 2, QTableWidgetItem(str(producto.get('Precio USD', ''))))

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
                
            version_file = os.path.join(base_path, 'version.txt')
            
            if not os.path.exists(version_file):
                # Fallback si no existe (ej. desarrollo)
                local_version = "0.0.0"
                logging.warning("No se encontró version.txt, usando 0.0.0")
            else:
                with open(version_file, 'r') as f:
                    local_version = f.read().strip()
            
            self.progress.emit(f"📌 Versión actual: {local_version}")
            
            # 2. Obtener versión remota de GitHub
            self.progress.emit("🌐 Conectando con GitHub...")
            repo_url = "https://api.github.com/repos/JoshuaMzV/Scrapping-Web"
            releases_url = f"{repo_url}/releases/tags/latest"
            
            response = requests.get(releases_url, timeout=10)
            if response.status_code != 200:
                self.finished.emit(False, "❌ No se encontró versión disponible en GitHub")
                return
            
            release_data = response.json()
            # IMPORTANTE: Usamos el Título (name) para la versión, ya que el tag siempre es 'latest'
            remote_version_str = release_data.get('name', 'v0.0.0')
            
            # Limpiar 'v' del inicio si existe
            remote_version = remote_version_str.lower().replace('v', '').strip()
            
            logging.info(f"Versión local: {local_version}, Remota: {remote_version}")
            
            if remote_version == local_version:
                self.finished.emit(False, f"✅ Ya tienes la versión más reciente: {local_version}")
                return
            
            # Comparación simple de strings (idealmente usar semver, pero esto funciona si formato es igual)
            # Si remote > local
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
        
        # Widget central con tabs
        self.tabs = QTabWidget()
        
        self.nike_tab = NikeTab()
        self.sephora_tab = SephoraTab()
        
        self.tabs.addTab(self.nike_tab, "👟 Nike")
        self.tabs.addTab(self.sephora_tab, "💄 Sephora")
        
        self.setCentralWidget(self.tabs)
        
        # Status bar con botón de actualización
        status_bar = self.statusBar()
        status_bar.showMessage(f"Catálogo Generator v{VERSION} - Listo")
        
        update_btn = QPushButton("🔄 Buscar Actualización")
        update_btn.setMaximumWidth(200)
        update_btn.clicked.connect(self.check_for_updates)
        status_bar.addPermanentWidget(update_btn)
        
        self.updater_worker = None
    
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


def main():
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
        raise


if __name__ == '__main__':
    main()
