# Sistema de Seguridad con Interfaz ESP8266

## 📋 Descripción

Sistema de seguridad biométrico integral que integra un lector de huellas dactilares con un módulo ESP8266 (NodeMCU) para control de acceso. El sistema incluye detección de movimiento mediante sensor PIR, gestión de usuarios, registro de eventos y notificaciones en tiempo real.

> [!CAUTION]
> **REQUISITO CRÍTICO: Conexión ESP8266**
> 
> La aplicación **NO SE PODRÁ ABRIR** si el módulo ESP8266 no está conectado y accesible. El sistema requiere comunicación activa con el ESP8266 desde el inicio para funcionar correctamente. Asegúrese de que el dispositivo esté encendido y conectado a la red antes de ejecutar la aplicación.

## ✨ Características Principales

### 🔐 Control de Acceso Biométrico
- **Registro de huellas dactilares**: Sistema de 4 huellas por usuario
- **Autenticación en tiempo real**: Verificación instantánea contra base de datos
- **Sincronización automática**: Actualización bidireccional entre base de datos y ESP8266
- **Gestión de permisos**: Sistema de roles y niveles de acceso

### 📡 Integración ESP8266
- **Comunicación HTTP**: Protocolo REST para comandos y consultas
- **Comandos soportados**:
  - `Registrar`: Captura de nuevas huellas
  - `Eliminar`: Borrado de huellas del sensor
  - `Consultar`: Verificación de huellas almacenadas
  - `PIR`: Activación del sensor de movimiento
  - `sql`: Sincronización de datos
  - `notificacion`: Envío de alertas
  - `puerta`: Control de cerradura electrónica

### 🚨 Sistema de Alertas
- **Detección de movimiento**: Sensor PIR con horarios programados
- **Accesos denegados**: Registro de intentos fallidos
- **Notificaciones del sistema**: Alertas en tiempo real mediante notificaciones de escritorio
- **Integración Slack**: Notificaciones remotas para eventos críticos
- **Historial completo**: Registro de todos los eventos de seguridad

### 👥 Gestión de Usuarios
- **Sistema de login**: Autenticación con cédula y contraseña
- **Roles y permisos**: Control granular de accesos
- **Perfiles de usuario**: Información detallada de cada usuario
- **Soporte técnico**: Sistema de tickets para problemas de acceso

### 📊 Monitoreo y Reportes
- **Historial de ingresos**: Registro de accesos por zona
- **Historial de alertas**: Seguimiento de eventos de seguridad
- **Interfaz gráfica**: Dashboard intuitivo con Flet

## 🔧 Requisitos del Sistema

### Hardware Requerido
- **ESP8266 (NodeMCU)**: Módulo configurado con el firmware del sistema de seguridad (proyecto separado)
- Los sensores y actuadores están conectados al ESP8266, no directamente a la computadora

### Software Requerido
- **Python**: 3.8 o superior
- **MySQL**: 5.7 o superior / MariaDB 10.3 o superior
- **Sistema Operativo**: Windows, Linux o macOS

## 📦 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Jhoan130702/interfaz_sistema_seguridad.git
cd interfaz_sistema_seguridad
```

> [!NOTE]
> Si descargó el proyecto como ZIP, extraiga el contenido y navegue a la carpeta del proyecto en su terminal.

### 2. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `flet==0.24.1` - Framework de interfaz gráfica
- `requests==2.32.3` - Comunicación HTTP con ESP8266
- `mysql-connector-python` - Conexión a base de datos
- `bcrypt==4.2.0` - Encriptación de contraseñas
- `plyer==2.1.0` - Notificaciones del sistema
- `python-dotenv==1.0.0` - Gestión de variables de entorno
- `reportlab==4.2.5` - Generación de reportes PDF

### 4. Configurar Variables de Entorno

Copie el archivo de ejemplo y configure sus valores:

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

Edite el archivo `.env` con sus configuraciones:

```env
# Configuración de Base de Datos MySQL
DB_HOST=localhost
DB_USER=root_remoto
DB_PASSWORD=tu_contraseña
DB_NAME=sistema_seguridad
DB_PORT=3306

# Configuración del ESP8266
ESP8266_URL=http://192.168.4.1/
```

> [!IMPORTANT]
> **Configuración del ESP8266**
> 
> La dirección IP del ESP8266 debe ser accesible desde su computadora. Por defecto, el ESP8266 crea un punto de acceso WiFi con la IP `192.168.4.1`. Asegúrese de:
> 1. Conectarse a la red WiFi del ESP8266
> 2. Verificar la conectividad con `ping 192.168.4.1`
> 3. Ajustar la URL en `.env` si usa una configuración diferente

### 5. Configurar Base de Datos

> [!IMPORTANT]
> **Archivos SQL Disponibles**
> 
> Los scripts SQL para crear la base de datos y todas las tablas necesarias están disponibles en Google Drive:
> 
> 📁 **[Descargar Scripts SQL](https://drive.google.com/drive/folders/1d_oRMVqGqehMLwGLFK8czLH_W27KYsLZ?usp=drive_link)**

#### Pasos para Configurar la Base de Datos

1. **Descargar los archivos SQL** desde el enlace de Google Drive
2. **Abrir MySQL** (puede usar MySQL Workbench, phpMyAdmin, o línea de comandos)
3. **Ejecutar los scripts** en el siguiente orden:
   - Script de creación de base de datos
   - Script de creación de tablas
   - Script de procedimientos almacenados (si aplica)
   - Script de datos iniciales (si aplica)

#### Usando MySQL desde Línea de Comandos

```bash
# Conectarse a MySQL
mysql -u root -p

# Ejecutar el script SQL
source ruta/al/archivo/script.sql

# O importar directamente
mysql -u root -p sistema_seguridad < ruta/al/archivo/script.sql
```

#### Usando MySQL Workbench

1. Abrir MySQL Workbench
2. Conectarse a su servidor MySQL
3. Ir a **File → Open SQL Script**
4. Seleccionar el archivo SQL descargado
5. Ejecutar el script (⚡ icono de rayo o Ctrl+Shift+Enter)

#### Verificar la Instalación

```sql
-- Conectarse a la base de datos
USE sistema_seguridad;

-- Verificar que las tablas se crearon correctamente
SHOW TABLES;

-- Debería mostrar:
-- - permisos
-- - usuario
-- - huella
-- -- historial_alerta
-- - ingresos_zona
-- - soporte
```

### 6. Configurar Conexión con ESP8266

> [!IMPORTANT]
> **Requisito Previo: ESP8266 Configurado**
> 
> El módulo ESP8266 debe estar previamente configurado con el firmware del sistema de seguridad (proyecto separado). Asegúrese de que:
> 1. El ESP8266 esté encendido y funcionando
> 2. Pueda conectarse a la red WiFi del ESP8266 (o que esté en su red local)
> 3. La dirección IP del ESP8266 sea accesible desde su computadora

**Verificar Conectividad:**

```bash
# Hacer ping a la IP del ESP8266 (por defecto 192.168.4.1)
ping 192.168.4.1
```

**Probar Conexión con Python:**

```python
import requests

ESP8266_URL = "http://192.168.4.1/"

try:
    response = requests.post(ESP8266_URL, data={"command": "Consultar"}, timeout=5)
    print(f"✓ Conexión exitosa: {response.text}")
except Exception as e:
    print(f"✗ Error de conexión: {e}")
```

Si la conexión es exitosa, puede proceder a ejecutar la aplicación.

## 🚀 Uso

### Iniciar la Aplicación

```bash
python run.py
```

O alternativamente:

```bash
python -m src.Main
```

### Primer Inicio

1. **Verificar conexión ESP8266**: Asegúrese de que el módulo esté encendido y accesible
2. **Conectarse a la red WiFi del ESP8266** (si usa modo AP)
3. **Ejecutar la aplicación**: `python run.py`
4. **Iniciar sesión** con credenciales de administrador
5. **Registrar usuarios** y sus huellas dactilares

### Flujo de Trabajo Típico

#### Registro de Nuevo Usuario

1. Acceder al módulo de gestión de usuarios
2. Ingresar datos del usuario (cédula, nombre, apellidos, etc.)
3. Asignar rol/permiso
4. Registrar 4 huellas dactilares
5. El sistema sincroniza automáticamente con el ESP8266

#### Verificación de Acceso

1. El usuario coloca su dedo en el sensor
2. El ESP8266 verifica la huella
3. Si coincide, envía el ID de huella al sistema
4. El sistema registra el ingreso en la base de datos
5. Se muestra notificación de acceso concedido/denegado

#### Monitoreo de Seguridad

- **Hilo 1** (cada 3 minutos): Sincroniza huellas entre BD y ESP8266
- **Hilo 2** (cada 5 segundos): Monitorea sensor PIR y lector de huellas
- **Hilo 3** (horarios programados): Activa/desactiva sensor PIR

## 📁 Estructura del Proyecto

```
Proyecto/
├── src/
│   ├── Main.py                 # Punto de entrada principal
│   ├── database/
│   │   └── DataBase.py         # Gestión de conexiones MySQL
│   ├── services/
│   │   ├── FuncionesEsp.py     # Comunicación con ESP8266
│   │   └── NotificacionesBarra.py  # Sistema de notificaciones
│   └── ui/
│       ├── Login.py            # Interfaz de inicio de sesión
│       ├── Aplicacion.py       # Dashboard principal
│       └── Perfil.py           # Gestión de perfiles
├── config/
│   └── config.py               # Carga de variables de entorno
├── assets/                     # Recursos gráficos
├── docs/                       # Documentación adicional
├── tests/                      # Pruebas unitarias
├── .env                        # Variables de entorno (NO subir a Git)
├── .env.example                # Plantilla de variables de entorno
├── requirements.txt            # Dependencias Python
├── run.py                      # Script de ejecución
└── README.md                   # Este archivo
```

## 🔄 Hilos de Ejecución

El sistema utiliza 3 hilos principales para operación continua:

### Hilo 1 - Sincronización de Huellas (MiHilo)
- **Frecuencia**: Cada 3 minutos (180.1 segundos)
- **Función**: Sincroniza huellas entre base de datos y ESP8266
- **Operaciones**:
  - Consulta huellas en BD
  - Consulta huellas en ESP8266
  - Elimina huellas huérfanas
  - Actualiza permisos de acceso

### Hilo 2 - Monitoreo en Tiempo Real (MiHilo2)
- **Frecuencia**: Cada 5 segundos
- **Función**: Monitorea sensores y eventos
- **Operaciones**:
  - Lee estado del sensor PIR
  - Verifica lecturas del sensor de huellas
  - Registra accesos concedidos/denegados
  - Genera notificaciones

### Hilo 3 - Activación Programada PIR (Pir)
- **Horarios**: 18:00, 19:00, 19:30
- **Función**: Activa sensor PIR en horarios específicos
- **Operaciones**:
  - Envía comando PIR al ESP8266
  - Registra activación en logs

## 🔐 Sistema de Permisos

El sistema maneja diferentes niveles de acceso:

| ID | Código | Descripción |
|----|--------|-------------|
| 1  | 000    | Administrador |
| 2-5| 333    | Personal Autorizado |
| 6  | 222    | Usuario Estándar |
| 7+ | 111    | Visitante |

## 🛠️ Solución de Problemas

### La aplicación no inicia

> [!WARNING]
> **Problema más común**: ESP8266 no conectado o no accesible

**Solución**:
1. Verificar que el ESP8266 esté encendido
2. Conectarse a la red WiFi del ESP8266 (o verificar que esté en su red local)
3. Hacer ping a la IP configurada: `ping 192.168.4.1`
4. Verificar que la URL en `.env` sea correcta
5. Revisar logs en consola para errores específicos
6. Ejecutar el script de prueba de conexión (ver sección anterior)

### Error de conexión a base de datos

**Solución**:
1. Verificar que MySQL esté ejecutándose
2. Comprobar credenciales en archivo `.env`
3. Verificar que la base de datos `sistema_seguridad` exista
4. Comprobar permisos del usuario de BD
5. Revisar el puerto de MySQL (por defecto 3306)

### No se registran huellas

**Solución**:
1. Verificar conexión con ESP8266
2. Revisar logs de la aplicación para errores
3. Asegurar que el usuario existe en la base de datos
4. Verificar que los hilos de sincronización estén activos
5. Comprobar que no haya huellas duplicadas

### Notificaciones no aparecen

**Solución**:
1. Verificar permisos de notificaciones del sistema operativo
2. Comprobar que `plyer` esté instalado correctamente
3. En Linux, instalar `notify-send`: `sudo apt-get install libnotify-bin`
4. En Windows, verificar que las notificaciones estén habilitadas

### Error "ESP8266 no responde"

**Solución**:
1. Verificar que el ESP8266 esté en la misma red
2. Comprobar la dirección IP en el archivo `.env`
3. Verificar que el firewall no esté bloqueando la conexión
4. Reiniciar el ESP8266
5. Verificar que el firmware del ESP8266 esté funcionando correctamente

## 📝 Notas Importantes

- **Seguridad**: Las contraseñas se almacenan con encriptación bcrypt
- **Backup**: Realice respaldos regulares de la base de datos
- **ESP8266**: El firmware del ESP8266 es un proyecto separado. Esta aplicación solo se comunica con él vía HTTP
- **Actualizaciones**: Mantenga sincronizadas las versiones del firmware ESP8266 y esta aplicación
- **Red**: La aplicación debe poder comunicarse con el ESP8266 en todo momento
- **Hilos**: El sistema usa 3 hilos en segundo plano para sincronización y monitoreo continuo

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Cree una rama para su característica (`git checkout -b feature/AmazingFeature`)
3. Commit sus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abra un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia que especifique el propietario del repositorio.

## 👨‍💻 Autor

**Jhoan130702**
- GitHub: [@Jhoan130702](https://github.com/Jhoan130702)
- Repositorio: [interfaz_sistema_seguridad](https://github.com/Jhoan130702/interfaz_sistema_seguridad)

## 📞 Soporte

Para reportar problemas o solicitar ayuda:
- Abra un [Issue en GitHub](https://github.com/Jhoan130702/interfaz_sistema_seguridad/issues)
- Use el sistema de soporte integrado en la aplicación
- Contacte al administrador del sistema

## 📚 Recursos Adicionales

### Archivos del Proyecto
- 📁 **[Scripts SQL de Base de Datos](https://drive.google.com/drive/folders/1d_oRMVqGqehMLwGLFK8czLH_W27KYsLZ?usp=drive_link)** - Todos los scripts necesarios para configurar la base de datos

### Documentación Relacionada
- 📖 **[Documentación de Variables de Entorno](docs/ENVIRONMENT_VARIABLES.md)** - Detalles sobre configuración de `.env`
- 📊 **[Diagrama del Sistema](docs/diagrama.md)** - Arquitectura y flujo de datos

### Tecnologías Utilizadas
- [Flet](https://flet.dev/) - Framework de UI multiplataforma
- [MySQL](https://www.mysql.com/) - Sistema de gestión de base de datos
- [Requests](https://requests.readthedocs.io/) - Librería HTTP para Python
- [bcrypt](https://github.com/pyca/bcrypt/) - Encriptación de contraseñas
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Gestión de variables de entorno

---

**Desarrollado con ❤️ usando Python y Flet**
