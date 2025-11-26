import requests
import json
import logging
import platform
import socket
import ctypes
import os
from datetime import datetime
from src.config.settings import DISCORD_WEBHOOK_URL, VERSION

def get_system_info():
    """Obtiene información básica del sistema para monitoreo."""
    try:
        # Info básica
        system_info = {
            "OS": f"{platform.system()} {platform.release()}",
            "PC Name": socket.gethostname(),
            "User": os.getlogin(),
            "Python": platform.python_version()
        }
        
        # Contar ventanas visibles (Windows API)
        def count_visible_windows():
            count = 0
            def enum_handler(hwnd, ctx):
                nonlocal count
                if ctypes.windll.user32.IsWindowVisible(hwnd):
                    count += 1
            
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
            ctypes.windll.user32.EnumWindows(WNDENUMPROC(enum_handler), 0)
            return count

        system_info["Open Windows"] = count_visible_windows()
        return system_info
    except Exception as e:
        return {"Error": str(e)}

def send_error_report(failed_urls, log_snippet=None, is_critical=False):
    """
    Envía un reporte de errores a Discord vía Webhook.
    :param failed_urls: Lista de tuplas (url, error_message) o solo urls
    :param log_snippet: Texto del log relevante (opcional)
    :param is_critical: Booleano, si es True marca el reporte como CRÍTICO
    """
    if not DISCORD_WEBHOOK_URL:
        logging.warning("No se ha configurado DISCORD_WEBHOOK_URL")
        return

    if not failed_urls and not is_critical:
        return

    try:
        # Título y Color según severidad
        title = "🚨 Reporte de Errores de Scraping"
        color = 15158332 # Rojo (0xE74C3C)
        
        if is_critical:
            title = "🔥 CRITICAL ERROR / CRASH DETECTED 🔥"
            color = 10038562 # Rojo Oscuro (0x992D22)

        # Construir el mensaje Embed
        embed = {
            "title": title,
            "description": f"Se encontraron **{len(failed_urls)}** problemas." if failed_urls else "Error crítico del sistema.",
            "color": color,
            "fields": [],
            "footer": {
                "text": f"Catálogo Generator v{VERSION} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }

        # 1. Información del Sistema (Monitoreo)
        sys_info = get_system_info()
        sys_info_str = "\n".join([f"**{k}:** {v}" for k, v in sys_info.items()])
        embed["fields"].append({
            "name": "🖥️ System Info",
            "value": sys_info_str,
            "inline": False
        })

        # 2. Log Snippet (si existe)
        if log_snippet:
            # Discord limita los values a 1024 caracteres
            log_clean = str(log_snippet)[-950:] # Tomar los últimos 950 caracteres
            embed["fields"].append({
                "name": "📜 Log Snippet",
                "value": f"```bash\n{log_clean}\n```",
                "inline": False
            })

        # 3. Detalles de los errores (limitado a 10 campos para no saturar si hay sys info)
        if failed_urls:
            for i, item in enumerate(failed_urls[:10]):
                url = item
                error = "Error desconocido"
                
                if isinstance(item, tuple) or isinstance(item, list):
                    url = item[0]
                    if len(item) > 1:
                        error = str(item[1])
                
                # Truncar error si es muy largo
                if len(error) > 100:
                    error = error[:97] + "..."

                embed["fields"].append({
                    "name": f"❌ Fallo #{i+1}",
                    "value": f"**URL:** {url}\n**Error:** {error}",
                    "inline": False
                })

            if len(failed_urls) > 10:
                 embed["fields"].append({
                    "name": "...",
                    "value": f"Y {len(failed_urls) - 10} errores más.",
                    "inline": False
                })

        payload = {
            "username": "Scraper Bot Monitor",
            "avatar_url": "https://cdn-icons-png.flaticon.com/512/2504/2504945.png",
            "embeds": [embed]
        }

        if is_critical:
            payload["content"] = "@here ⚠️ **CRITICAL SYSTEM FAILURE**"

        response = requests.post(
            DISCORD_WEBHOOK_URL, 
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 204:
            logging.info("✅ Reporte de error enviado a Discord exitosamente")
        else:
            logging.error(f"❌ Error enviando a Discord: {response.status_code} - {response.text}")

    except Exception as e:
        logging.error(f"❌ Excepción al enviar reporte a Discord: {e}")
