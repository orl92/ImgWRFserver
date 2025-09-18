#!/bin/bash

# Activar entorno virtual
source /home/omar/GitHub/ImgWRFserver/.venv/bin/activate

# Ejecutar worker de Celery
celery -A meteo_server worker --loglevel=info --concurrency=4 &

# Ejecutar beat de Celery
celery -A meteo_server beat --loglevel=info &