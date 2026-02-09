# station_data/data/OpenFileObs.py - Versión mejorada con más logs
from datetime import datetime
import os
import re

from station_data.data.FileObs import FileObs


class OpenFileObs:
    def __init__(self, station_number, hour):
        self.__hour = hour
        self.__station_number = station_number
        fileobs = FileObs()
        self.__filename = fileobs.descargar_archivos_por_hora(self.__hour, self.__station_number)
        fileobs.limpiar_directorio_temporal()

        print(f"DEBUG: Archivo descargado: {self.__filename}")
        print(f"DEBUG: Existe archivo: {os.path.exists(self.__filename)}")

        # Leer el archivo con codificación adecuada
        with open(self.__filename, 'r', encoding='utf-8', errors='ignore') as f:
            self.__file_content = f.read()

        print(f"DEBUG: Contenido del archivo:\n{self.__file_content}")

        # Parsear el contenido
        self.__parse_content()

        print(f"DEBUG: Datos parseados: {self.__parsed_data}")

    def __parse_content(self):
        """Parsea el contenido del archivo SYNOP"""
        lines = self.__file_content.strip().split('\n')

        # Filtrar líneas vacías
        lines = [line.strip() for line in lines if line.strip()]

        print(f"DEBUG: Líneas después de limpiar: {lines}")

        # Eliminar líneas que solo contengan NNNN
        lines = [line for line in lines if line != 'NNNN']

        if not lines:
            print("DEBUG: No hay líneas válidas después de filtrar NNNN")
            self.__parsed_data = {}
            return

        # La primera línea es el encabezado AAXX
        header_line = lines[0]
        header_parts = header_line.split()

        print(f"DEBUG: Header line: {header_line}")
        print(f"DEBUG: Header parts: {header_parts}")

        if len(header_parts) >= 2 and header_parts[0] == 'AAXX':
            # Extraer fecha y hora del encabezado (formato: AAXX ddhhw)
            date_code = header_parts[1]
            print(f"DEBUG: Date code: {date_code}")
            if len(date_code) >= 4:
                day = date_code[0:2]  # Día del mes
                hour_code = date_code[2:4]  # Hora UTC
                print(f"DEBUG: Día extraído: {day}, Hora extraída: {hour_code}")
            else:
                day = datetime.utcnow().strftime('%d')
                hour_code = self.__hour
                print(f"DEBUG: Usando día/hora por defecto: {day}, {hour_code}")
        else:
            day = datetime.utcnow().strftime('%d')
            hour_code = self.__hour
            print(f"DEBUG: Header no válido, usando día/hora por defecto: {day}, {hour_code}")

        # Buscar la línea que contiene los datos de la estación
        station_line = None
        station_str = str(self.__station_number)
        station_line_index = -1

        for i, line in enumerate(lines):
            # Buscar el número de estación al inicio de la línea
            if line.startswith(station_str) or f' {station_str} ' in line:
                station_line = line
                station_line_index = i
                print(f"DEBUG: Encontrada línea de estación en índice {i}: {line}")
                break

        if not station_line:
            print(f"DEBUG: No se encontró línea para estación {station_str}")
            self.__parsed_data = {}
            return

        # Unir todas las líneas siguientes hasta encontrar una que termine con '='
        full_station_data = station_line
        i = station_line_index + 1
        while i < len(lines) and not full_station_data.endswith('='):
            full_station_data += ' ' + lines[i]
            i += 1

        print(f"DEBUG: Datos completos de estación: {full_station_data}")

        # Eliminar el '=' al final si existe
        if full_station_data.endswith('='):
            full_station_data = full_station_data[:-1].strip()
            print(f"DEBUG: Datos sin '=': {full_station_data}")

        # Separar sección 1 y sección 3 (si existe)
        # La sección 3 comienza con '333'
        if '333' in full_station_data:
            # Dividir por '333' pero mantener el '333' en la segunda parte
            parts = full_station_data.split('333', 1)
            sesion1 = parts[0].strip()
            sesion2 = '333 ' + parts[1].strip() if parts[1].strip() else None
            print(f"DEBUG: Sesión 1: {sesion1}")
            print(f"DEBUG: Sesión 2: {sesion2}")
        else:
            sesion1 = full_station_data.strip()
            sesion2 = None
            print(f"DEBUG: Solo sesión 1 (no hay '333'): {sesion1}")

        self.__parsed_data = {
            'day': day,
            'hour': hour_code,
            'number': self.__station_number,
            'sesion1': sesion1,
            'sesion2': sesion2,
            'raw_content': self.__file_content,
            'lines': lines,
            'full_station_data': full_station_data
        }

    @property
    def hour(self):
        return self.__hour

    @property
    def station_number(self):
        return self.__station_number

    @property
    def filename(self):
        return self.__filename

    @filename.setter
    def filename(self, value):
        self.__filename = value

    def openFile(self):
        # Para compatibilidad con código existente
        return self.__file_content.split('\n')

    def obs(self):
        """Método para compatibilidad - devuelve las líneas procesadas"""
        return self.__parsed_data.get('lines', [])

    def station(self):
        """Devuelve los datos parseados de la estación"""
        return self.__parsed_data

    def get_raw_content(self):
        """Devuelve el contenido crudo del archivo"""
        return self.__file_content

    def get_parsed_data(self):
        """Devuelve los datos parseados"""
        return self.__parsed_data