# Django Meteo Simulation API

Esta API permite gestionar y visualizar simulaciones meteorológicas, generando y recuperando imágenes de variables meteorológicas específicas.

## 🌟 Características

* 📊 Listado de todas las simulaciones disponibles
* 🌤️ Generación de gráficos meteorológicos
* 🖼️ Recuperación de imágenes existentes para simulaciones y variables específicas
* 💾 Almacenamiento eficiente con eliminación automática de archivos
* 🔄 Evita duplicados: si ya existen imágenes para una simulación y variable, devuelve las existentes
* ⚡ Comandos de gestión para generación masiva de imágenes
* 🔐 Almacenamiento seguro de la `SECRET_KEY` mediante cifrado (Fernet)
* 🗄️ Soporte para múltiples bases de datos: SQLite (desarrollo) y PostgreSQL/MySQL (producción)

## 🚀 Instalación y configuración

### Requisitos previos

```bash
# Clona el repositorio
git clone <tu-repo>
cd ImgWRFserver

# Crea y activa un entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Instala las dependencias
pip install -r requirements.txt

### Configuración del entorno
El proyecto utiliza un archivo `.env` para almacenar las variables de configuración (incluyendo la `SECRET_KEY` cifrada). Para generarlo automáticamente, ejecuta:
```bash
python manage.py setup_env
```
Este comando interactivo te guiará para configurar:

Claves de cifrado (`ENCRYPTION_KEY` y `SECRET_KEY` cifrada).

Configuración básica (`DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`).

Base de datos (opción entre `SQLite` o `PostgreSQL`/`MySQL`).

`Celery`/`Redis` (URLs del broker y backend).

Correo electrónico (opcional, para envío de emails).

Si solo necesitas generar las claves (sin crear el archivo `.env`), usa:
`
```bash
python manage.py setup_env --only-keys
```
Importante: La `SECRET_KEY` original (sin cifrar) se muestra al final del proceso. Guárdala en un lugar seguro (gestor de contraseñas), nunca la incluyas en el `.env`.

Estructura del archivo `.env` generado

```ini
# Archivo de configuración de entorno para Django Meteo Simulation API
# Generado automáticamente por el comando setup_env

ENCRYPTION_KEY=5Xk0Z9y8W7q6L2j4R1t3B8nA6cV9fG7hJ3kM2pQ5s=
SECRET_KEY=gAAAAABm...
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
# Si elegiste PostgreSQL, aparecerán:
DB_ENGINE=django.db.backends.postgresql
DB_NAME=mi_bd
DB_USER=usuario
DB_PASSWORD=contraseña
DB_HOST=localhost
DB_PORT=5432
# Si configuraste email:
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña
EMAIL_USE_TLS=True
```

**Migraciones y archivos estáticos**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

### 📋 Comandos de gestión
La aplicación incluye comandos personalizados para generar datos meteorológicos de prueba.

**Generar imágenes meteorológicas**
```bash
# Fecha actual, todas las variables y horas 00,06,12,18
python manage.py generate_images

# Fecha específica
python manage.py generate_images --date 20231015

# Variables específicas
python manage.py generate_images --variables T2,rh2,ws10

# Horas específicas
python manage.py generate_images --hours 00,12

# Combinar opciones
python manage.py generate_images --date 20231015 --variables T2,ws10 --hours 00,12
```
**Generar observaciones de estaciones**
```bash
# Generar una observación por estación activa
python manage.py generate_test_observations --date=20240115 --hour=12

# Generar 5 observaciones para estaciones específicas
python manage.py generate_test_observations --date=20240115 --hour=12 --stations=78350,78351 --count=5

# Vista previa sin guardar
python manage.py generate_test_observations --date=20240115 --hour=06 --verbose --dry-run

# Forzar regeneración
python manage.py generate_test_observations --date=20240115 --hour=18 --force
```

## 🌐 Endpoints de la API
La documentación interactiva (Swagger) está disponible en la raíz del proyecto: `http://localhost:8000/`

Todos los endpoints de la API están prefijados con `/api/`.

### 1. Listar simulaciones y obtener imágenes

**URL:** `/api/simulations/`  
**Método:** `GET`

- **Sin parámetros:** devuelve la lista de todas las simulaciones disponibles (ordenadas por fecha descendente).
- **Con parámetros (`datetime_init` y `var_name`):** devuelve las URLs de las imágenes para esa simulación y variable.

| Parámetro      | Formato     | Ejemplo       | Obligatorio |
|----------------|-------------|---------------|-------------|
| `datetime_init`| YYYYMMDDHH  | `2025091512`  | Sí (para obtener imágenes) |
| `var_name`     | string      | `T2`          | Sí (para obtener imágenes) |

**Ejemplo de solicitud:**

```bash
curl "http://localhost:8000/api/simulations/?datetime_init=2025091512&var_name=T2"
```

**Ejemplo de respuesta (con parámetros):**

```json
{
    "status": "success",
    "simulation_date": "2025-09-15T12:00:00+00:00",
    "variable_name": "T2",
    "image_urls": [
        "http://localhost:8000/media/meteo_plots/20250915_120000/T2/imagen_1.png",
        "http://localhost:8000/media/meteo_plots/20250915_120000/T2/imagen_2.png"
    ],
    "count": 2
}
```
### 2. Datos de estaciones meteorológicas

**URL:** `/api/station-data/`  
**Método:** `GET`

Devuelve los datos actuales de las estaciones meteorológicas registradas en el sistema.

**Ejemplo de solicitud:**

```bash
curl http://localhost:8000/api/station-data/
```

**Ejemplo de respuesta:**

```json
{
    "status": "success",
    "count": 2,
    "data": [
        {
            "id": 1,
            "code": "78350",
            "name": "Estación Central",
            "latitude": 23.12,
            "longitude": -82.38,
            "temperature": 25.3,
            "humidity": 78,
            "wind_speed": 5.2,
            "timestamp": "2025-02-16T12:00:00Z"
        },
        {
            "id": 2,
            "code": "78351",
            "name": "Estación Costera",
            "latitude": 23.05,
            "longitude": -82.55,
            "temperature": 24.8,
            "humidity": 81,
            "wind_speed": 6.1,
            "timestamp": "2025-02-16T12:00:00Z"
        }
    ]
}
```

**Nota:** Los campos y valores mostrados son ilustrativos; la estructura real puede variar según la implementación de tu modelo de datos.

## 🗃️ Modelos de datos
  
### Simulation:
`initial_datetime`: Fecha y hora de inicio de la simulación (única).

`created_at`: Fecha de creación del registro.

`description`: Descripción opcional.

### MeteoImage:
`simulation`: ForeignKey a Simulation.

`valid_datetime`: Fecha y hora válida de la imagen.

`variable_name`: Nombre de la variable (ej. T2).

`image`: Archivo de imagen (almacenado en media/).

`data_min`, `data_max`, `data_mean`: Estadísticas de los datos representados.

## 📁 Estructura de almacenamiento de imágenes

Las imágenes se guardan en:

```text
media/
    meteo_plots/
        YYYYMMDD_HHMMSS/          # Fecha de la simulación
            nombre_variable/       # Ej. T2, rh2
                imagen_1.png
                imagen_2.png
```

## 🧪 Entornos de desarrollo y producción

El proyecto está diseñado para funcionar con diferentes configuraciones según el entorno:

**Desarrollo:** Usa SQLite (por defecto) y `DEBUG=True`. El archivo .env puede generarse con setup_env eligiendo SQLite.

**Producción:** Define las variables de entorno directamente en el sistema (o en un .env seguro) con `DEBUG=False`, `ALLOWED_HOSTS` adecuados y `DB_ENGINE`, `DB_NAME`, etc., para `PostgreSQL`/`MySQL`.

**Ejemplo de configuración para producción con** `PostgreSQL`:

```ini
DEBUG=False
ALLOWED_HOSTS=midominio.com,www.midominio.com
CSRF_TRUSTED_ORIGINS=https://midominio.com
DB_ENGINE=django.db.backends.postgresql
DB_NAME=produccion_db
DB_USER=usuario_prod
DB_PASSWORD=contraseña_segura
DB_HOST=localhost
DB_PORT=5432
```

## 🚀 Despliegue con Nginx y Gunicorn

### 1. Instalar dependencias del sistema y de Python
```bash
sudo apt update
sudo apt install nginx python3-pip python3-venv redis-server
pip install gunicorn
```
### 2. Configurar Gunicorn como servicio systemd
Crea el archivo `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=gunicorn daemon for Django Meteo API
After=network.target

[Service]
User=tu_usuario
Group=www-data
WorkingDirectory=/ruta/a/tu/proyecto
EnvironmentFile=/ruta/a/tu/proyecto/.env
ExecStart=/ruta/a/tu/entorno/bin/gunicorn --access-logfile - --workers 3 --bind unix:/ruta/a/tu/proyecto/app.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Habilita e inicia el servicio:**

```bash
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```
### 3. Configurar Nginx
Crea `/etc/nginx/sites-available/meteo-api`:

```nginx
server {
    listen 80;
    server_name tu_dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /ruta/a/tu/proyecto/staticfiles/;
    }

    location /media/ {
        alias /ruta/a/tu/proyecto/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/ruta/a/tu/proyecto/app.sock;
    }
}
```

**Activa el sitio y prueba:**

```bash
sudo ln -s /etc/nginx/sites-available/meteo-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. Configurar SSL con Let's Encrypt (recomendado)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu_dominio.com
```

## 📝 Notas finales

**Seguridad:** La SECRET_KEY nunca está en texto plano en el repositorio; se cifra con ENCRYPTION_KEY.

**Base de datos:** El proyecto usa SQLite por defecto para desarrollo. Para producción, configura PostgreSQL/MySQL a través de las variables de entorno.

**Redis:** Necesario para Celery. Asegúrate de que Redis esté instalado y en ejecución.

**Documentación interactiva:** Accede a / para Swagger UI, donde podrás probar todos los endpoints.

## 🤝 Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un issue para discutir cambios importantes antes de enviar un pull request.

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.
