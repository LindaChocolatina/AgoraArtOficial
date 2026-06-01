#!/usr/bin/env python
import os
from dotenv import load_dotenv

load_dotenv()

# Desarrollo local: SQLite por defecto (evita colgar si el túnel DBeaver está cerrado).
if os.environ.get('FLASK_ENV', 'development') == 'development':
    if not os.environ.get('DATABASE_URL') and not os.environ.get('USE_POSTGRES'):
        os.environ.setdefault('USE_SQLITE', '1')

from app.factories.app_factory import create_app

# Determinar el entorno de configuración
config_name = os.environ.get('FLASK_ENV', 'development')

# Crear la aplicación usando el factory pattern
app = create_app(config_name)

if __name__ == '__main__':
    # Configuración para desarrollo
    debug_mode = config_name == 'development'
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Art Platform Backend iniciando en modo {config_name}")
    print(f"Debug: {debug_mode}")
    print(f"Port: {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode
    )