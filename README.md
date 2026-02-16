# Django Meteo Simulation API

Esta API permite gestionar y visualizar simulaciones meteorológicas, generando y recuperando imágenes de variables meteorológicas específicas.

## 🌟 Características

* 📊 Listado de todas las simulaciones disponibles
* 🌤️ Generación de gráficos meteorológicos
* 🖼️ Recuperación de imágenes existentes para simulaciones y variables específicas
* 💾 Almacenamiento eficiente con eliminación automática de archivos
* 🔄 Evita duplicados: si ya existen imágenes para una simulación y variable, devuelve las existentes
* ⚡ Comandos de gestión para generación masiva de imágenes
* 🔐 Almacenamiento seguro de la SECRET_KEY mediante cifrado

## 🚀 Instalación y configuración

### Requisitos previos

```bash
pip install django pillow requests numpy matplotlib cartopy gunicorn cryptography
```

### Configuración de la base de datos

En `settings.py` (ya configurado):

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

### Configuración de URLs

En el archivo principal `urls.py`:

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

## 🔐 Configuración segura de la SECRET_KEY

Por razones de seguridad, la `SECRET_KEY` de Django se almacena cifrada en el archivo `.env` en lugar de texto plano. Para ello se utiliza la librería `cryptography` y un comando personalizado de Django.

### Generación de claves

Ejecuta el siguiente comando en la raíz del proyecto:

```bash
python manage.py generate_secret_key --update-env
```

Este comando:
1. Genera una clave de cifrado maestra (`ENCRYPTION_KEY`).
2. Genera una `SECRET_KEY` aleatoria de Django y la cifra con la clave anterior.
3. Actualiza (o crea) tu archivo `.env` con las variables:
   - `ENCRYPTION_KEY`
   - `SECRET_KEY` (valor cifrado)

**Opciones adicionales:**
- `--show-only`: Muestra las claves sin modificar el archivo `.env`.
- `--env-file RUTA`: Especifica un archivo `.env` diferente (por defecto: `.env`).

### ¿Cómo funciona internamente?

En `settings.py` se define una función `decrypt_secret_key` que utiliza `Fernet` para descifrar el valor de `SECRET_KEY` usando `ENCRYPTION_KEY`. Si las variables de entorno faltan o el descifrado falla, Django lanza una excepción y no arranca.

### Importante

- La `ENCRYPTION_KEY` es tan sensible como la propia `SECRET_KEY`. Guárdala también en un gestor de contraseñas.
- Nunca subas tu archivo `.env` al repositorio (debe estar en `.gitignore`).
- Si cambias la `ENCRYPTION_KEY`, deberás volver a cifrar la `SECRET_KEY` y actualizar el `.env`.

## 📋 Comandos de gestión

La aplicación incluye comandos personalizados para generar datos e imágenes.

### Uso básico

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

# Generar observaciones de prueba
python manage.py generate_test_observations --date=20240115 --hour=12

# Generar 5 observaciones para estaciones específicas
python manage.py generate_test_observations --date=20240115 --hour=12 --stations=78350,78351 --count=5

# Ver información detallada sin guardar
python manage.py generate_test_observations --date=20240115 --hour=06 --verbose --dry-run

# Forzar regeneración incluso si ya existen datos
python manage.py generate_test_observations --date=20240115 --hour=18 --force
```

### Parámetros disponibles

| Parámetro | Descripción | Valor por defecto |
|-----------|-------------|-------------------|
| `--date` | Fecha en formato YYYYMMDD | Fecha actual |
| `--variables` | Lista de variables separadas por comas | Todas las variables |
| `--hours` | Lista de horas (HH) separadas por comas | 00,06,12,18 |

### Variables disponibles

```
['T2', 'td2', 'rh2', 'RAINC', 'RAINC3H', 'slp', 'PSFC', 'ws10', 'wd10', 'clflo', 'clfmi', 'clfhi', 'mcape', 'mcin', 'lcl', 'lfc', 'NOAHRES', 'SWDOWN', 'GLW', 'SWNORM', 'OLR']
```

## 🌐 Endpoints de la API

### 1. Listar simulaciones / Obtener imágenes

**URL:** `/simulations/`  
**Método:** `GET`

Sin parámetros: devuelve lista de simulaciones ordenadas por fecha descendente.

Con parámetros: devuelve las URLs de las imágenes para una simulación y variable específicas.

**Parámetros:**
- `datetime_init`: Fecha y hora en formato YYYYMMDDHH (ej: 2025091512)
- `var_name`: Nombre de la variable meteorológica (ej: T2)

**Ejemplo de respuesta:**
```json
{
    "status": "success",
    "simulation_date": "2025-09-15T12:00:00+00:00",
    "variable_name": "T2",
    "image_urls": [
        "http://example.com/media/meteo_plots/20250915_120000/T2/image1.png"
    ],
    "count": 1
}
```

### 2. Generar gráficos

**URL:** `/generate-plot/`  
**Método:** `POST`

Genera y guarda imágenes para una simulación y variable específicas. Si ya existen, devuelve las existentes.

**Cuerpo (JSON):**
```json
{
    "datetime_init": "2025-09-15T12:00:00",
    "var_name": "T2"
}
```

## 🗃️ Modelos de datos

- **Simulation**: `initial_datetime` (única), `created_at`, `description`.
- **MeteoImage**: Relación con `Simulation`, `valid_datetime`, `variable_name`, `image`, estadísticas.

## 📁 Estructura de almacenamiento

```
media/
    meteo_plots/
        YYYYMMDD_HHMMSS/
            variable_name/
                imagen1.png
                imagen2.png
```

## 💻 Uso típico

```bash
# Generar imágenes para una simulación
curl -X POST -H "Content-Type: application/json" \
  -d '{"datetime_init": "2025-09-15T12:00:00", "var_name": "T2"}' \
  http://localhost:8000/api/generate-plot/

# Listar simulaciones
curl http://localhost:8000/api/simulations/

# Obtener imágenes para una simulación específica
curl "http://localhost:8000/api/simulations/?datetime_init=2025091512&var_name=T2"
```

## 🚀 Despliegue con Nginx y Gunicorn

### 1. Instalar Nginx y Gunicorn
```bash
sudo apt update
sudo apt install nginx
pip install gunicorn
```

### 2. Configurar Gunicorn (systemd)

Crea `/etc/systemd/system/gunicorn.service`:

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

Crea `/etc/nginx/sites-available/tu_app`:

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

Habilitar y reiniciar:
```bash
sudo ln -s /etc/nginx/sites-available/tu_app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Configurar SSL con Let's Encrypt (opcional)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu_dominio.com
```

## 📝 Notas importantes

- Las fechas deben seguir el formato especificado.
- El sistema evita duplicación de imágenes.
- Los archivos se eliminan automáticamente al borrar sus registros.
- Las simulaciones se ordenan por fecha descendente por defecto.

## 🌦️ Ejemplos de variables meteorológicas

| Variable | Descripción |
|----------|-------------|
| T2 | Temperatura a 2 metros |
| td2 | Temperatura de punto de rocío |
| rh2 | Humedad relativa |
| ws10 | Velocidad del viento a 10 metros |
| wd10 | Dirección del viento a 10 metros |

## 🛠️ Soporte

Para reportar problemas o solicitar características, abre un issue en el repositorio.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.