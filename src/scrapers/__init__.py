# Scrapers package - alias hacia archivos en raíz
import sys
import os

# Agregar el directorio padre al path para importar desde raíz
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar desde la ubicación original (raíz del proyecto)
try:
    from scrapers.nike import scrape_nike, calcular_precios as nike_calcular, limpiar_precio as nike_limpiar
    from scrapers.sephora import scrape_sephora, calcular_precios as sephora_calcular, limpiar_precio as sephora_limpiar
except ImportError:
    # Si no funciona, usar importlib como fallback
    import importlib.util
    scrapers_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    spec = importlib.util.spec_from_file_location("nike", 
        os.path.join(scrapers_dir, "scrapers", "nike.py"))
    nike = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nike)
    
    scrape_nike = nike.scrape_nike
    nike_calcular = nike.calcular_precios
    nike_limpiar = nike.limpiar_precio

__all__ = [
    'scrape_nike',
    'scrape_sephora',
    'nike_calcular',
    'sephora_calcular',
    'nike_limpiar',
    'sephora_limpiar'
]
