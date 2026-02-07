# Configuración de Variables de Entorno

Este proyecto utiliza variables de entorno para gestionar configuraciones sensibles como credenciales de base de datos y URLs de dispositivos.

## Archivos de Configuración

### `.env`
Contiene las variables de entorno reales. **NO debe compartirse ni subirse a Git** (ya está en `.gitignore`).

### `.env.example`
Plantilla de ejemplo que muestra qué variables se necesitan sin exponer valores sensibles.

### `config/config.py`
Módulo centralizado que carga y proporciona acceso a las variables de entorno.

## Variables Disponibles

### Base de Datos MySQL
- `DB_HOST`: Host del servidor MySQL (default: `localhost`)
- `DB_USER`: Usuario de la base de datos (default: `root`)
- `DB_PASSWORD`: Contraseña del usuario (default: vacío)
- `DB_NAME`: Nombre de la base de datos (default: `sistema_seguridad`)
- `DB_PORT`: Puerto de MySQL (default: `3306`)

### ESP8266
- `ESP8266_URL`: URL base del dispositivo ESP8266 (default: `http://192.168.4.1/`)

## Configuración Inicial

1. **Copiar el archivo de ejemplo:**
   ```bash
   copy .env.example .env
   ```

2. **Editar `.env` con tus valores:**
   ```env
   DB_HOST=localhost
   DB_USER=tu_usuario
   DB_PASSWORD=tu_contraseña
   DB_NAME=sistema_seguridad
   DB_PORT=3306
   
   ESP8266_URL=http://192.168.4.1/
   ```

3. **Instalar python-dotenv:**
   ```bash
   pip install -r requirements.txt
   ```

## Uso en el Código

### Opción 1: Usar el módulo config (Recomendado)
```python
from config.config import DB_HOST, DB_USER, ESP8266_URL

# Usar las variables
print(f"Conectando a {DB_HOST}")
```

### Opción 2: Acceso directo con os.getenv
```python
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('DB_HOST', 'localhost')
```

## Archivos Modificados

Los siguientes archivos fueron actualizados para usar variables de entorno:

- **`src/database/DataBase.py`**: Conexión a MySQL usando variables de entorno
- **`src/services/FuncionesEsp.py`**: URL del ESP8266 desde variable de entorno
- **`config/config.py`**: Módulo centralizado de configuración (NUEVO)

## Seguridad

> [!WARNING]
> Nunca compartas el archivo `.env` ni lo subas a repositorios públicos. Contiene credenciales sensibles.

> [!IMPORTANT]
> El archivo `.env` ya está incluido en `.gitignore` para evitar commits accidentales.
