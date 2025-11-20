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
from datetime import datetime
from io import BytesIO
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QProgressBar,
    QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, QSpinBox,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QUrl
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
import pandas as pd

# Importar funciones de scraping
from scrapers.nike import scrape_nike, calcular_precios as nike_calcular, limpiar_precio as nike_limpiar
from scrapers.sephora import scrape_sephora, calcular_precios as sephora_calcular, limpiar_precio as sephora_limpiar
from src.config.settings import VERSION

# Importar Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait


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
            
            # Inicializar driver
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 20)
            
            datos_encontrados = []
            
            # Determinar scraper
            if 'nike' in self.marca.lower():
                scraper_func = scrape_nike
                calcular = nike_calcular
            elif 'sephora' in self.marca.lower():
                scraper_func = scrape_sephora
                calcular = sephora_calcular
            else:
                self.error.emit(f"Marca '{self.marca}' no soportada")
                return

            for idx, url in enumerate(self.urls, 1):
                self.progress.emit(f"[{idx}/{len(self.urls)}] Procesando: {url}")
                
                try:
                    datos_extraidos = scraper_func(self.driver, self.wait, url)
                    
                    if datos_extraidos and datos_extraidos.get('nombre') != 'Error':
                        precio_usd = float(datos_extraidos['precio'].replace(',', '.').replace('$', '').replace(',', ''))
                        precios = calcular(precio_usd)
                        
                        row = {
                            'Nombre': datos_extraidos['nombre'],
                            'Sitio': datos_extraidos.get('sitio', 'Desconocido'),
                            'Precio USD': precio_usd,
                            **precios
                        }
                        datos_encontrados.append(row)
                        self.progress.emit(f"✅ {datos_extraidos['nombre']}")
                    else:
                        self.progress.emit(f"❌ Error extrayendo datos de {url}")
                        
                except Exception as e:
                    self.progress.emit(f"❌ Error: {str(e)}")
                    continue

            self.driver.quit()
            
            if datos_encontrados:
                self.finished.emit({
                    'success': True,
                    'data': datos_encontrados,
                    'count': len(datos_encontrados)
                })
            else:
                self.error.emit("No se extrajeron datos")
                
        except Exception as e:
            if self.driver:
                self.driver.quit()
            self.error.emit(f"Error: {str(e)}")


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
        
        # Status bar
        self.statusBar().showMessage(f"Catálogo Generator v{VERSION} - Listo")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
