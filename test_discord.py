import sys
import os
import logging

# Configurar path
sys.path.append(os.getcwd())

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

print("Importing discord_notifier...")
try:
    from utils.discord_notifier import send_error_report
    print("Import successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

print("Testing send_error_report...")
try:
    failed_urls = [
        ("https://example.com/bad-url", "Error 404: Not Found"),
        ("https://google.com/error", "Connection Timeout")
    ]
    send_error_report(failed_urls)
    print("send_error_report executed successfully.")
except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()
