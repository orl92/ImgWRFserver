import os
import django
import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from wrf_img.utils.plot_generators import generate_and_save_meteo_plot

import warnings
warnings.filterwarnings('ignore')


class Command(BaseCommand):
    help = 'Genera imágenes meteorológicas para todas las variables y horas disponibles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Fecha en formato YYYYMMDD (por defecto: hoy)',
        )
        parser.add_argument(
            '--variables',
            type=str,
            help='Lista de variables separadas por comas (por defecto: todas)',
        )
        parser.add_argument(
            '--hours',
            type=str,
            help='Lista de horas separadas por comas (por defecto: 00,06,12,18)',
        )

    def handle(self, *args, **options):
        # Procesar argumentos
        target_date = options.get('date')
        if target_date:
            now = datetime.datetime.strptime(target_date, '%Y%m%d')
        else:
            now = datetime.datetime.now()

        # Procesar variables
        variables_input = options.get('variables')
        if variables_input:
            variables = [v.strip() for v in variables_input.split(',')]
        else:
            variables = [
                'T2', 'td2', 'rh2', 'RAINC', 'RAINC3H', 'slp', 'PSFC',
                'ws10', 'wd10', 'clflo', 'clfmi', 'clfhi', 'mcape', 'mcin', 'lcl',
                'lfc', 'NOAHRES', 'SWDOWN', 'GLW', 'SWNORM', 'OLR',
            ]

        # Procesar horas
        hours_input = options.get('hours')
        if hours_input:
            hours = [h.strip().zfill(2) for h in hours_input.split(',')]
        else:
            hours = ['00', '06', '12', '18']

        # Validar horas
        valid_hours = []
        for hour in hours:
            try:
                hour_int = int(hour)
                if 0 <= hour_int <= 23:
                    valid_hours.append(hour.zfill(2))
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Hora inválida: {hour}. Debe estar entre 00 y 23.')
                    )
            except ValueError:
                self.stdout.write(
                    self.style.WARNING(f'Hora inválida: {hour}. Debe ser un número entre 00 y 23.')
                )

        if not valid_hours:
            self.stdout.write(
                self.style.ERROR('No se proporcionaron horas válidas. Usando horas por defecto: 00,06,12,18')
            )
            valid_hours = ['00', '06', '12', '18']

        # Ejecutar la generación de imágenes
        success_count = 0
        error_count = 0

        for variable in variables:
            for hour in valid_hours:
                date_str = now.strftime('%Y%m%d')
                datetime_init = date_str + hour

                try:
                    self.stdout.write(f"Generando imágenes para {variable} a las {hour}:00...")
                    result = generate_and_save_meteo_plot(datetime_init, variable)
                    success_count += len(result)
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {len(result)} imágenes generadas para {variable} a las {hour}:00')
                    )

                except Exception as e:
                    error_count += 1
                    self.stdout.write(
                        self.style.ERROR(f'✗ Error procesando {variable} a las {hour}:00 - {str(e)}')
                    )

        # Resumen de la ejecución
        self.stdout.write(
            self.style.SUCCESS(
                f'Proceso completado. Éxitos: {success_count}, Errores: {error_count}'
            )
        )