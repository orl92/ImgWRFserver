#!/bin/bash

DJANGODIR=$(cd `dirname $0` && pwd)
# Definir el valor de --hours según la hora actual
HORA=$(date +%H)
case $HORA in
  04) HOURS_ARG="00" ;;
  10) HOURS_ARG="06" ;;
  16) HOURS_ARG="12" ;;
  22) HOURS_ARG="18" ;;
  *) echo "Hora no configurada: $HORA"; exit 1 ;;
esac

# Navegar al directorio del proyecto (opcional, si es necesario)
# cd /ruta/al/proyecto

# Ejecutar el comando con el argumento correspondiente
${DJANGODIR}/.venv/bin/python manage.py generate_images --hours $HOURS_ARG