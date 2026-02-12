#!/bin/bash

DJANGODIR=$(cd `dirname $0` && pwd)

# Obtener la hora actual
HORA=$(date +%H)
# Obtener la fecha actual en formato YYYYMMDD
FECHA=$(date +%Y%m%d)

# Definir el valor de --hour según la hora actual
case $HORA in
  00|01|02)
    HOUR_ARG="00"
    ;;
  03|04|05)
    HOUR_ARG="03"
    ;;
  06|07|08)
    HOUR_ARG="06"
    ;;
  09|10|11)
    HOUR_ARG="09"
    ;;
  12|13|14)
    HOUR_ARG="12"
    ;;
  15|16|17)
    HOUR_ARG="15"
    ;;
  18|19|20)
    HOUR_ARG="18"
    ;;
  21|22|23)
    HOUR_ARG="21"
    ;;
  *)
    echo "Hora no válida: $HORA"
    exit 1
    ;;
esac

# Ejecutar el comando con la fecha actual y la hora correspondiente
${DJANGODIR}/.venv/bin/python ${DJANGODIR}/manage.py import_weather_data --date $FECHA --hour $HOUR_ARG

# Opcional: Log de la ejecución
if [ $? -eq 0 ]; then
    echo "$(date): Datos importados correctamente para fecha $FECHA, hora $HOUR_ARG"
else
    echo "$(date): ERROR al importar datos para fecha $FECHA, hora $HOUR_ARG"
    exit 1
fi