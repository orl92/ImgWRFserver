#!/bin/bash

# Definir el valor de --hours según la hora actual
HORA=$(date +%H)
case $HORA in
  04) HOURS_ARG="00" ;;
  10) HOURS_ARG="06" ;;
  16) HOURS_ARG="12" ;;
  22) HOURS_ARG="18" ;;
  *) echo "Hora no configurada: $HORA"; exit 1 ;;
esac

# Ejecutar el comando con el argumento correspondiente
python manage.py generate_images --hours $HOURS_ARG