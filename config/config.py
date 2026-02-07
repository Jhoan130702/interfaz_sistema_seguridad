"""
Módulo de configuración para variables de entorno
Carga las variables de entorno y proporciona acceso centralizado
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

# Configuración de Base de Datos
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'sistema_seguridad')
DB_PORT = os.getenv('DB_PORT', '3306')

# Configuración del ESP8266
ESP8266_URL = os.getenv('ESP8266_URL', 'http://192.168.4.1/')
