# config.py - Configuración para aplicación IMD Desktop
import os
import socket

class ProductionConfig:
    """Configuración para entorno de producción"""
    
    # Configuración de base de datos - se adapta automáticamente por PC
    @staticmethod
    def get_db_config():
        """Retorna configuración de DB según la PC"""
        hostname = socket.gethostname().upper()
        
        # Configuraciones específicas por PC/Estación
        db_configs = {
            # Estación 1 - Línea AXIAL
            'PC-AXIAL-01': {
                'host': '192.168.1.100',  # IP del servidor MySQL local
                'user': 'imd_user',
                'password': 'imd_password',
                'database': 'imd_production',
                'machine_default': 'AXIAL'
            },
            
            # Estación 2 - Línea RADIAL  
            'PC-RADIAL-01': {
                'host': '192.168.1.100',
                'user': 'imd_user', 
                'password': 'imd_password',
                'database': 'imd_production',
                'machine_default': 'RADIAL'
            },
            
            # Configuración por defecto (desarrollo/otras PCs)
            'DEFAULT': {
                'host': '127.0.0.1',
                'user': 'root',
                'password': '',
                'database': 'imd_local',
                'machine_default': 'AXIAL'
            }
        }
        
        # Buscar configuración específica o usar default
        config = db_configs.get(hostname, db_configs['DEFAULT'])
        
        return {
            'host': config['host'],
            'user': config['user'],
            'password': config['password'],
            'database': config['database'],
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': True,
            'machine_default': config['machine_default']
        }
    
    # Configuración de aplicación
    APP_NAME = "IMD Material Control"
    APP_VERSION = "1.0.1"
    
    # Configuración de ventana
    WINDOW_CONFIG = {
        'width': 1920,  # Tamaño completo
        'height': 1080,
        'min_size': (1200, 800),
        'resizable': False,  # No redimensionable
        'fullscreen': False,
        'maximized': True,   # Iniciar maximizada
        'on_top': False
    }
    
    # Configuración de icono
    @staticmethod
    def get_icon_path():
        """Retorna la ruta del icono de la aplicación"""
        icon_path = os.path.join(os.path.dirname(__file__), 'icono_app.png')
        return icon_path if os.path.exists(icon_path) else None
    
    # Configuración de logs
    LOG_CONFIG = {
        'level': 'INFO',
        'file_path': os.path.join(os.path.expanduser('~'), 'IMD_Logs', 'app.log'),
        'max_size': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5
    }
    
    # URLs y puertos
    FLASK_HOST = '127.0.0.1'
    FLASK_DEBUG = False
    
    @staticmethod
    def get_app_data_dir():
        """Directorio para datos de la aplicación"""
        app_dir = os.path.join(os.path.expanduser('~'), 'IMD_MaterialControl')
        os.makedirs(app_dir, exist_ok=True)
        return app_dir