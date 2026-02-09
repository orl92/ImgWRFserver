# station_data/management/commands/import_weather_data.py
import os
import sys
from datetime import datetime, time
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

try:
    from station_data.data.GetData import GetData
    from station_data.models import WeatherObservation, Station, Province, Town
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
    from station_data.data.GetData import GetData
    from station_data.models import WeatherObservation, Station, Province, Town


class Command(BaseCommand):
    help = 'Importa datos meteorológicos desde las estaciones para una fecha y hora específicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            required=True,
            help='Fecha en formato YYYYMMDD (ej: 20240115)'
        )
        parser.add_argument(
            '--hour',
            type=str,
            required=True,
            help='Hora en formato HH (ej: 00, 03, 06, 09, 12, 15, 18, 21)'
        )
        parser.add_argument(
            '--stations',
            type=str,
            required=False,
            help='Lista de estaciones separadas por comas (ej: 78350,78351,78352). Si no se especifica, usa todas las estaciones.'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar reimportación incluso si los datos ya existen'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué datos se importarían sin guardar en la base de datos'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Mostrar información detallada de debug'
        )
        parser.add_argument(
            '--auto-create-stations',
            action='store_true',
            help='Crear estaciones automáticamente si no existen en la BD'
        )

    def handle(self, *args, **options):
        date_str = options['date']
        hour_str = options['hour']
        stations_str = options['stations']
        force = options['force']
        dry_run = options['dry_run']
        debug = options['debug']
        auto_create_stations = options['auto_create_stations']

        # Validar fecha
        try:
            observation_date = datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError:
            raise CommandError('Formato de fecha inválido. Use YYYYMMDD (ej: 20240115)')

        # Validar hora
        valid_hours = ["00", "03", "06", "09", "12", "15", "18", "21"]
        if hour_str not in valid_hours:
            raise CommandError(f'Hora inválida. Use una de: {", ".join(valid_hours)}')

        # Convertir hora a objeto time
        try:
            hour_time = time(int(hour_str), 0)
        except ValueError:
            raise CommandError('Hora inválida. Use formato HH (ej: 06, 12, 18)')

        # Parsear lista de estaciones
        stations_list = None
        if stations_str:
            try:
                stations_list = [int(s.strip()) for s in stations_str.split(',')]
                self.stdout.write(f"Procesando estaciones específicas: {stations_list}")
            except ValueError:
                raise CommandError('Formato de estaciones inválido. Use números separados por comas (ej: 78350,78351)')

        # Crear objeto GetData
        get_data = GetData()

        # Si se especificaron estaciones, sobreescribir la lista
        if stations_list:
            get_data._GetData__numbers_stations = stations_list

        self.stdout.write(
            self.style.SUCCESS(
                f"Iniciando importación para {observation_date} a las {hour_str}:00"
            )
        )

        if debug:
            self.stdout.write(f"MODO DEBUG ACTIVADO")
            self.stdout.write(f"Estaciones a procesar: {get_data._GetData__numbers_stations}")

        stats = {
            'total': 0,
            'imported': 0,
            'skipped': 0,
            'failed': 0,
            'success': 0,
            'error': 0,
            'stations_created': 0
        }

        # Procesar cada estación individualmente
        for station_number in get_data._GetData__numbers_stations:
            stats['total'] += 1

            try:
                self.stdout.write(f"\n{'=' * 60}")
                self.stdout.write(f"Procesando estación {station_number}...")

                # Obtener datos de la estación
                station_data = get_data.get_station(hour_str, station_number)

                if debug:
                    self.stdout.write(f"Datos recibidos de get_station: {station_data}")

                # VERIFICACIÓN USANDO LA CLAVE 'status'
                status = station_data.get('status', 'error')

                if status == 'error':
                    error_message = station_data.get('message', 'Error desconocido')
                    self.stdout.write(
                        self.style.WARNING(f"  Estación {station_number}: Error - {error_message}")
                    )
                    stats['skipped'] += 1
                    stats['error'] += 1
                    continue

                # Si llegamos aquí, status == 'success'
                stats['success'] += 1

                # Extraer datos del diccionario
                station_id = station_data['estacion']

                # BUSCAR O CREAR LA ESTACIÓN EN LA BASE DE DATOS
                station_obj = self._get_or_create_station(
                    station_id, station_number, auto_create_stations, debug
                )

                if not station_obj:
                    error_msg = f"No se encontró estación {station_id} y auto-create está desactivado"
                    self.stdout.write(
                        self.style.WARNING(f"  Estación {station_id}: {error_msg}")
                    )
                    stats['skipped'] += 1
                    continue

                if station_obj and not station_obj.id:
                    # Estación recién creada
                    stats['stations_created'] += 1

                # Verificar si ya existe la observación
                if not force:
                    exists = WeatherObservation.objects.filter(
                        station=station_obj,
                        date=observation_date,
                        hour=hour_time
                    ).exists()

                    if exists:
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Estación {station_id}: Datos ya existen (usa --force para reimportar)"
                            )
                        )
                        stats['skipped'] += 1
                        continue

                # Parsear fecha de observación
                obs_date_str = station_data.get('dia', '')
                obs_hour_str = station_data.get('hora', '')

                if debug:
                    self.stdout.write(f"  Fecha cruda de observación: {obs_date_str}")
                    self.stdout.write(f"  Hora cruda de observación: {obs_hour_str}")

                try:
                    # Convertir fecha (formato dd/mm/YYYY)
                    if obs_date_str:
                        obs_date = datetime.strptime(obs_date_str, '%d/%m/%Y').date()
                    else:
                        obs_date = observation_date

                    # Convertir hora (formato 12h a 24h)
                    if obs_hour_str:
                        try:
                            # Intentar formato 12h (ej: 07:00 AM)
                            obs_hour_24h = datetime.strptime(obs_hour_str, '%I:%M %p').time()
                        except ValueError:
                            try:
                                # Intentar formato 24h (ej: 12:00)
                                obs_hour_24h = datetime.strptime(obs_hour_str, '%H:%M').time()
                            except ValueError:
                                # Usar la hora de la observación
                                obs_hour_24h = hour_time
                    else:
                        obs_hour_24h = hour_time

                except (ValueError, TypeError) as e:
                    if debug:
                        self.stdout.write(f"  WARN: Error parseando fecha/hora: {e}")
                    obs_date = observation_date
                    obs_hour_24h = hour_time

                if debug:
                    self.stdout.write(f"  Fecha parseada: {obs_date}")
                    self.stdout.write(f"  Hora parseada: {obs_hour_24h}")

                # Función helper para limpiar valores
                def clean_value(value):
                    if value in [None, '--', 'traza', 'Traza', 'TRAZA', '', 'NaN']:
                        return None
                    if isinstance(value, str):
                        value = value.strip()
                        if value.lower() == 'traza':
                            return 0.1  # Valor para traza
                        try:
                            value = value.replace(',', '.')
                            return float(value)
                        except (ValueError, TypeError):
                            return value
                    return value

                # Preparar datos para el modelo
                observation_data = {
                    'station': station_obj,
                    'station_number': station_id,
                    'date': obs_date,
                    'hour': obs_hour_24h,
                    'temperature': clean_value(station_data.get('temperatura')),
                    'max_temperature': clean_value(station_data.get('temperatura maxima')),
                    'min_temperature': clean_value(station_data.get('temperatura minima')),
                    'relative_humidity': clean_value(station_data.get('humedad relativa')),
                    'wind_speed': clean_value(station_data.get('velocidad del viento')),
                    'wind_direction': station_data.get('direccion del viento'),
                    'wind_direction_degrees': clean_value(station_data.get('dd')),
                    'precipitation_3h': clean_value(station_data.get('precipitacion en 3 horas')),
                    'precipitation_24h': clean_value(station_data.get('precipitacion en 24 horas')),
                    'cloud_coverage': clean_value(station_data.get('cielo cubierto')),
                    'sky_condition': station_data.get('estado del cielo'),

                    # Nuevos campos de tiempo
                    'current_weather_code': station_data.get('tiempo_presente_codigo'),
                    'current_weather_description': station_data.get('tiempo_presente_descripcion'),
                    'past_weather1_code': station_data.get('tiempo_pasado1_codigo'),
                    'past_weather1_description': station_data.get('tiempo_pasado1_descripcion'),
                    'past_weather2_code': station_data.get('tiempo_pasado2_codigo'),
                    'past_weather2_description': station_data.get('tiempo_pasado2_descripcion'),

                    # Campos adicionales
                    'dew_point': clean_value(station_data.get('punto_rocio')),
                    'pressure_station': clean_value(station_data.get('presion_estacion')),
                    'pressure_sea_level': clean_value(station_data.get('presion_nivel_mar')),
                    'visibility': clean_value(station_data.get('visibilidad_km')),  # ← Nueva visibilidad

                    'observation_date_utc': timezone.now(),
                }

                # Asegurar que wind_speed sea un float
                if observation_data['wind_speed'] and isinstance(observation_data['wind_speed'], str):
                    try:
                        observation_data['wind_speed'] = float(observation_data['wind_speed'])
                    except ValueError:
                        observation_data['wind_speed'] = None

                if debug:
                    self.stdout.write("Datos procesados para guardar:")
                    for key, value in observation_data.items():
                        if key != 'station':  # No mostrar el objeto station completo
                            self.stdout.write(f"  {key}: {value} ({type(value).__name__})")

                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [DRY RUN] Estación {station_id}: Datos listos para importar"
                        )
                    )
                    stats['imported'] += 1
                else:
                    try:
                        # Crear o actualizar registro
                        obj, created = WeatherObservation.objects.update_or_create(
                            station=station_obj,
                            date=obs_date,
                            hour=obs_hour_24h,
                            defaults=observation_data
                        )

                        action = "Creado" if created else "Actualizado"
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  Estación {station_id}: {action} correctamente (ID: {obj.id})"
                            )
                        )
                        stats['imported'] += 1

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  ERROR al guardar en BD: {str(e)}")
                        )
                        import traceback
                        if debug:
                            self.stdout.write(f"  Traceback: {traceback.format_exc()}")
                        stats['failed'] += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR en estación {station_number}: {str(e)}")
                )
                import traceback
                if debug:
                    self.stdout.write(f"  Traceback: {traceback.format_exc()}")
                stats['failed'] += 1

        # Mostrar resumen
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("RESUMEN DE IMPORTACIÓN"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"Total de estaciones procesadas: {stats['total']}")
        self.stdout.write(f"Estaciones con éxito (status=success): {stats['success']}")
        self.stdout.write(f"Estaciones con error (status=error): {stats['error']}")
        self.stdout.write(f"Estaciones creadas en BD: {stats['stations_created']}")
        self.stdout.write(f"Estaciones importadas/actualizadas: {stats['imported']}")
        self.stdout.write(f"Estaciones omitidas: {stats['skipped']}")
        self.stdout.write(f"Estaciones con error en BD: {stats['failed']}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nMODO DRY RUN: No se guardaron datos en la base de datos"
                )
            )

        if stats['imported'] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n¡Importación completada con éxito! {stats['imported']} observaciones guardadas."
                )
            )
        elif stats['total'] > 0 and stats['imported'] == 0:
            self.stdout.write(
                self.style.WARNING(
                    "\nAdvertencia: No se importaron datos. Verifica los archivos descargados."
                )
            )

    def _get_or_create_station(self, station_number, original_station_number, auto_create, debug=False):
        """
        Busca una estación en la base de datos o la crea si auto_create está activado
        """
        try:
            # Primero intentar buscar por número
            station = Station.objects.get(number=station_number)
            if debug:
                self.stdout.write(f"  ✅ Estación encontrada: {station.name} (ID: {station.id})")
            return station
        except Station.DoesNotExist:
            # Si no existe y auto_create está activado, crear una estación básica
            if auto_create:
                try:
                    # Buscar una provincia por defecto (la primera disponible)
                    default_province = Province.objects.first()

                    # Crear estación con datos básicos
                    station = Station.objects.create(
                        number=station_number,
                        name=f"Estación {station_number}",
                        latitude=0.0,  # Valores por defecto
                        longitude=0.0,
                        province=default_province,
                        is_active=True,
                        station_type='synoptic'
                    )

                    if debug:
                        self.stdout.write(f"  🆕 Estación creada: {station.name} (ID: {station.id})")

                    return station

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"  ERROR al crear estación: {str(e)}")
                    )
                    return None
            else:
                return None
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"  ERROR buscando estación: {str(e)}")
            )
            return None