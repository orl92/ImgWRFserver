# Django Meteo Simulation API
Esta API permite gestionar y visualizar simulaciones meteorológicas, generando y recuperando imágenes de variables meteorológicas específicas.

# Características
* Listado de todas las simulaciones disponibles
* Generación de gráficos meteorológicos
* Recuperación de imágenes existentes para simulaciones y variables específicas
* Almacenamiento eficiente con eliminación automática de archivos
* Evita duplicados: si ya existen imágenes para una simulación y variable, devuelve las existentes
*  Comandos de gestión para generación masiva de imágenes

# Instalación y configuración
## Requisitos previos
```bash
pip install django pillow requests numpy matplotlib cartopy gunicorn
```
### Configuración de la base de datos
En ```settings.py```:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

### Configuración segura de la SECRET_KEY
Por razones de seguridad, la ```SECRET_KEY``` de Django no se almacena en texto plano en el archivo ```.env```, sino cifrada mediante la librería ```cryptography```. De esta forma, aunque alguien obtuviera tu archivo ```.env```, no podría usar directamente la clave secreta.

Requisito adicional
Instala la dependencia necesaria para el cifrado:

```bash
pip install cryptography
```
Generación de claves
La primera vez que configures el proyecto (o cuando necesites regenerar la ```SECRET_KEY```), ejecuta el script ```generate_secret.py``` que se encuentra en la carpeta ```common```/:

```bash
python common/generate_secret.py
```
Este script realizará tres acciones:

Generará una clave de cifrado maestra (```ENCRYPTION_KEY```).

Generará una ```SECRET_KEY``` aleatoria de Django.

Cifrará la ```SECRET_KEY``` usando la clave maestra y mostrará el resultado.

La salida será similar a esta:

```text
Guarda esto en tu .env como ENCRYPTION_KEY:
5Xk0Z9y8W7q6L2j4R1t3B8nA6cV9fG7hJ3kM2pQ5s=

SECRET_KEY en texto plano (NO la guardes así):
django-insecure-&amp;42...

Guarda esto en tu .env como SECRET_KEY (valor cifrado):
gAAAAABm...
```
Configuración del archivo ```.env```
Copia los valores impresos y agrégalos a tu archivo ```.env``` (si no existe, créalo en la raíz del proyecto):

```ini
ENCRYPTION_KEY=5Xk0Z9y8W7q6L2j4R1t3B8nA6cV9fG7hJ3kM2pQ5s=
SECRET_KEY=gAAAAABm...
# El resto de variables (DEBUG, ALLOWED_HOSTS, etc.)
```
Importante:

La ```ENCRYPTION_KEY``` es tan sensible como la propia ```SECRET_KEY```. No la pierdas, guárdala también en un lugar seguro (gestor de contraseñas) por si necesitas recuperar el acceso.

Nunca subas tu archivo ```.env``` al repositorio (ya debería estar en ```.gitignore```).

Si cambias la ```ENCRYPTION_KEY```, deberás volver a cifrar la ```SECRET_KEY``` y actualizar el archivo ```.env```.

¿Cómo funciona internamente?
En ```settings.py``` se define una función ```decrypt_secret_key``` que utiliza ```cryptography.fernet.Fernet``` para descifrar el valor de ```SECRET_KEY``` usando ```ENCRYPTION_KEY```. Esta función se llama al cargar la configuración, de modo que Django siempre trabaja con la clave original en memoria.

Si por algún motivo las variables de entorno faltan o el descifrado falla, Django lanzará una excepción ```ImproperlyConfigured``` y no arrancará, evitando así el uso de una clave inválida.

Nota sobre regeneración de claves
Si en el futuro necesitas cambiar la ```SECRET_KEY``` (por ejemplo, por una rotación de seguridad), repite el proceso con el script ```generate_secret.py```. Asegúrate de mantener la misma ```ENCRYPTION_KEY``` a menos que quieras cambiar también la clave maestra (en cuyo caso deberás actualizar todas las claves cifradas). Recuerda que cambiar la ```SECRET_KEY``` invalidará todas las sesiones existentes, t```okens CSRF```, etc., por lo que debe hacerse con cuidado.

### Configuración de URLs
En el archivo principal ```urls.py```:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... tus otras URLs ...
    path('api/', include('wrf_img.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```
### Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```
# Comandos de gestión
La aplicación incluye un comando personalizado para generar imágenes meteorológicas de forma masiva.

## Uso básico
```bash
# Generar imágenes para la fecha actual y todas las variables
python manage.py generate_meteo_images

# Generar imágenes para una fecha específica
python manage.py generate_meteo_images --date 20231015

# Generar imágenes solo para variables específicas
python manage.py generate_meteo_images --variables T2,rh2,ws10

# Generar imágenes para horas específicas
python manage.py generate_meteo_images --hours 00,12

# Combinar todas las opciones
python manage.py generate_meteo_images --date 20231015 --variables T2,ws10 --hours 00,12

# Generar una observación por estación activa
python manage.py generate_test_observations --date=20240115 --hour=12

# Generar 5 observaciones para estaciones específicas
python manage.py generate_test_observations --date=20240115 --hour=12 --stations=78350,78351 --count=5

# Ver información detallada sin guardar
python manage.py generate_test_observations --date=20240115 --hour=06 --verbose --dry-run

# Forzar regeneración incluso si ya existen datos
python manage.py generate_test_observations --date=20240115 --hour=18 --force
```
## Parámetros disponibles
### Parámetro	Descripción	Valor por defecto
* ```--date```:	Fecha en formato YYYYMMDD ```(ej: 20231015)```	Fecha actual
* ```--variables```:	Lista de variables separadas por comas	Todas las variables disponibles
* ```--hours```:	Lista de horas separadas por comas ```(formato HH)```	00,06,12,18
## Variables disponibles
Las siguientes variables meteorológicas están disponibles para generación:

```python
[
    'T2', 'td2', 'rh2', 'RAINC', 'RAINC3H', 'slp', 'PSFC',
    'ws10', 'wd10', 'clflo', 'clfmi', 'clfhi', 'mcape', 'mcin', 'lcl',
    'lfc', 'NOAHRES', 'SWDOWN', 'GLW', 'SWNORM', 'OLR',
]
```
# Endpoints de la API
### 1. Listar simulaciones / Obtener imágenes
URL: ```/simulations/```

Método: ```GET```

Sin parámetros
Devuelve una lista de todas las simulaciones disponibles ordenadas por fecha descendente.

Ejemplo de respuesta:

```json
{
    "status": "success",
    "simulations": [
        "2025-09-15T12:00:00+00:00",
        "2025-09-15T10:00:00+00:00"
    ],
    "count": 2
}
```
### Con parámetros
Devuelve las URLs de las imágenes para una simulación y variable específicas.

### Parámetros:
```datetime_init```: Fecha y hora en formato YYYYMMDDHH ```(ej: 2025091512)```

```var_name```: Nombre de la variable meteorológica ```(ej: T2)```

### Ejemplo de solicitud:

```text
GET /simulations/?datetime_init=2025091512&var_name=T2
```
### Ejemplo de respuesta:

```json
{
    "status": "success",
    "simulation_date": "2025-09-15T12:00:00+00:00",
    "variable_name": "T2",
    "image_urls": [
        "http://example.com/media/meteo_plots/20250915_120000/T2/image1.png",
        "http://example.com/media/meteo_plots/20250915_120000/T2/image2.png"
    ],
    "count": 2
}
```
### 2. Generar gráficos
URL: ```/generate-plot/```

Método: ```POST```

Genera y guarda imágenes para una simulación y variable específicas. Si ya existen imágenes para esa combinación, devuelve las existentes.

### Cuerpo de la solicitud (JSON):

```json
{
    "datetime_init": "2025-09-15T12:00:00",
    "var_name": "T2"
}
```
### Ejemplo de respuesta exitosa:

```json
{
    "status": "success",
    "image_urls": [
        "http://example.com/media/meteo_plots/20250915_120000/T2/image1.png"
    ],
    "message": "Se generó 1 imagen"
}
```
### Ejemplo de respuesta cuando ya existen imágenes:

```json
{
    "status": "success",
    "image_urls": [
        "http://example.com/media/meteo_plots/20250915_120000/T2/image1.png"
    ],
    "message": "Ya existen 1 imágenes para esta simulación y variable"
}
```
# Modelos de datos
## Simulation
* ```initial_datetime```: Fecha y hora inicial de la simulación (única)

* ```created_at```: Fecha de creación del registro

* ```description```: Descripción opcional de la simulación

## MeteoImage
* ```simulation```: Relación con la simulación

* ```valid_datetime```: Fecha y hora válida de la imagen

* ```variable_name```: Nombre de la variable meteorológica

* ```image```: Archivo de imagen almacenado

* ```data_min, data_max, data_mean```: Estadísticas de los datos

# Estructura de almacenamiento
Las imágenes se almacenan en la siguiente estructura:

```text
media/
    meteo_plots/
        YYYYMMDD_HHMMSS/    # Fecha de la simulación
            variable_name/  # Nombre de la variable
                imagen1.png
                imagen2.png
```
# Uso típico
Generar imágenes para una nueva simulación:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"datetime_init": "2025-09-15T12:00:00", "var_name": "T2"}' http://localhost:8000/api/generate-plot/
```
Listar todas las simulaciones disponibles:
```bash
curl http://localhost:8000/api/simulations/
```
Obtener imágenes para una simulación específica:
```bash
curl "http://localhost:8000/api/simulations/?datetime_init=2025091512&var_name=T2"
```
# Manejo de errores
La API devuelve códigos de estado HTTP apropiados y mensajes de error descriptivos:

* ```400 Bad Request```: Parámetros faltantes o formato incorrecto
* ```404 Not Found```: Recurso no encontrado
* ```500 Internal Server Error```: Error interno del servidor

# Notas importantes
* Las fechas deben seguir el formato especificado para cada endpoint

* El sistema evita la duplicación de imágenes para la misma simulación y variable

* Los archivos de imagen se eliminan automáticamente cuando se borran sus registros

* Las imágenes se sirven a través de la URL de medios de Django

* Las simulaciones se ordenan por fecha descendente por defecto

# Ejemplos de variables meteorológicas
### Variable	Descripción
* ```T2```	Temperatura a 2 metros
* ```td2```	Temperatura de punto de rocío
* ```rh2```	Humedad relativa
* ```RAINC```	Precipitación acumulada
* ```ws10```	Velocidad del viento a 10 metros
* ```wd10```	Dirección del viento a 10 metros

# Despliegue con Nginx y Gunicorn
### 1. Instalar Nginx y Gunicorn
```bash
sudo apt update
sudo apt install nginx
pip install gunicorn
```
### 2. Configurar Gunicorn
Crear un archivo de servicio para Gunicorn en /etc/systemd/system/gunicorn.service:

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=tu_usuario
Group=www-data
WorkingDirectory=/ruta/a/tu/proyecto
ExecStart=/ruta/a/tu/entorno/bin/gunicorn --access-logfile - --workers 3 --bind unix:/ruta/a/tu/proyecto/app.sock config.wsgi:application

[Install]
WantedBy=multi-user.target
```
### 3. Configurar Nginx
Crear un archivo de configuración para Nginx en /etc/nginx/sites-available/tu_app:

```nginx
server {
    listen 80;
    server_name tu_dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /ruta/a/tu/proyecto;
    }
    
    location /media/ {
        root /ruta/a/tu/proyecto;
    }
    
    location / {
        include proxy_params;
        proxy_pass http://unix:/ruta/a/tu/proyecto/app.sock;
    }
}
```
### Habilitar el sitio:

```bash
sudo ln -s /etc/nginx/sites-available/tu_app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```
### 4. Configurar firewall
```bash
sudo ufw allow 'Nginx Full'
```
### 5. Iniciar y habilitar los servicios
```bash
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl restart nginx
```
### 6. Configurar SSL con Let's Encrypt (opcional)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu_dominio.com
```

# Soporte
Para reportar problemas o solicitar características, por favor abra un issue en el repositorio del proyecto.

# Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.