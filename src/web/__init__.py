# Web package
from flask import Flask

def create_app():
    """Factory function para crear la aplicación Flask"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Importar configuración
    from src.config import FLASK_HOST, FLASK_PORT, UPLOAD_FOLDER, MAX_CONTENT_LENGTH
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    # Registrar blueprints
    from .routes import api_bp
    app.register_blueprint(api_bp)
    
    return app
