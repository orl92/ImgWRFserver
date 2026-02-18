import random
from datetime import datetime, time

from django.core.management.base import BaseCommand
from django.utils import timezone
from station_data.models import Station, WeatherObservation


class Command(BaseCommand):
    help = 'Genera observaciones meteorológicas aleatorias para pruebas'

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
            help='Lista de estaciones separadas por comas (ej: 78350,78351,78352). Si no se especifica, usa todas las estaciones activas.'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar recreación incluso si los datos ya existen'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Número de observaciones por estación (por defecto: 1)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar qué datos se generarían sin guardar en la base de datos'
        )

    def handle(self, *args, **options):
        date_str = options['date']
        hour_str = options['hour']
        stations_str = options['stations']
        force = options['force']
        count = options['count']
        verbose = options['verbose']
        dry_run = options['dry_run']

        # Validar fecha
        try:
            observation_date = datetime.strptime(date_str, '%Y%m%d').date()
        except ValueError:
            raise CommandError('Formato de fecha inválido. Use YYYYMMDD (ej: 20240115)')

        # Validar hora
        try:
            hour_time = time(int(hour_str), 0, 0)
        except ValueError:
            raise CommandError('Hora inválida. Use formato HH (ej: 06, 12, 18)')

        # Obtener estaciones
        if stations_str:
            station_numbers = [int(s.strip()) for s in stations_str.split(',')]
            stations = Station.objects.filter(
                number__in=station_numbers,
                is_active=True
            )
        else:
            stations = Station.objects.filter(is_active=True)

        if not stations.exists():
            self.stdout.write(self.style.WARNING("No se encontraron estaciones activas."))
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Generando {count} observación(es) aleatoria(s) por estación para {observation_date} {hour_str}:00"
            )
        )
        self.stdout.write(f"Estaciones a procesar: {stations.count()}")

        # Listas de valores para generación aleatoria
        wind_directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                           'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', None]

        sky_conditions = [
            'Despejado', 'Poco nuboso', 'Intervalos nubosos', 'Nuboso',
            'Muy nuboso', 'Cubierto', 'Niebla', 'Lluvia débil', 'Lluvia moderada',
            'Lluvia fuerte', 'Tormenta', 'Chubascos', None
        ]

        weather_codes = ['00', '01', '02', '03', '04', '10', '11', '12', '13',
                         '14', '15', '16', '17', '18', '20', '21', '22', '23',
                         '24', '25', '26', '27', '28', '29', '30', '31', '32',
                         '33', '34', '35', '40', '41', '42', '43', '44', '45',
                         '46', '47', '48', '49', '50', '51', '52', '53', '54',
                         '55', '56', '57', '58', '59', '60', '61', '62', '63',
                         '64', '65', '66', '67', '68', '70', '71', '72', '73',
                         '74', '75', '76', '77', '78', '80', '81', '82', '83',
                         '84', '85', '86', '87', '88', '89', '90', '91', '92',
                         '93', '94', '95', '96', '97', '98', '99']

        weather_descriptions = [
            'Sin tiempo significativo', 'Nubes disipándose', 'Estado del cielo sin cambio',
            'Nubes formándose', 'Visibilidad reducida por humo', 'Lluvia leve',
            'Lluvia moderada', 'Lluvia fuerte', 'Tormenta', 'Neblina', 'Niebla',
            'Chubascos', 'Granizo', 'Nieve', 'Aguanieve', 'Rocío', 'Escarcha',
            'Ventisca', 'Huracán', 'Tornado', None
        ]

        cloud_types = ['CL', 'CM', 'CH', 'ST', 'SC', 'CU', 'CB', 'NS', 'AC',
                       'AS', 'CC', 'CS', 'CI', None]

        stats = {
            'total_created': 0,
            'total_skipped': 0,
            'total_stations': stations.count(),
            'total_observations': 0
        }

        for station in stations:
            self.stdout.write(f"\n{'=' * 60}")
            self.stdout.write(f"Estación: {station.name} (#{station.number})")

            for i in range(count):
                stats['total_observations'] += 1

                # Ajustar hora para múltiples observaciones
                current_hour = hour_time
                if count > 1:
                    # Para múltiples observaciones, usar horas diferentes
                    hour_offset = random.randint(0, 23)
                    current_hour = time(hour_offset, 0, 0)

                # Verificar si ya existe la observación
                if not force:
                    exists = WeatherObservation.objects.filter(
                        station=station,
                        date=observation_date,
                        hour=current_hour
                    ).exists()

                    if exists:
                        if verbose:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"  Observación {i + 1}: Ya existe para {current_hour} (usa --force para regenerar)"
                                )
                            )
                        stats['total_skipped'] += 1
                        continue

                # Generar datos aleatorios realistas
                base_temp = random.uniform(20.0, 32.0)  # Temperatura base
                temp_variation = random.uniform(-3.0, 3.0)

                observation_data = {
                    'station': station,
                    'station_number': station.number,
                    'date': observation_date,
                    'hour': current_hour,

                    # Temperaturas
                    'temperature': round(base_temp + temp_variation, 1),
                    'max_temperature': round(base_temp + random.uniform(2.0, 6.0), 1),
                    'min_temperature': round(base_temp - random.uniform(2.0, 6.0), 1),
                    'dew_point': round(base_temp - random.uniform(5.0, 15.0), 1),

                    # Humedad
                    'relative_humidity': random.randint(40, 95),

                    # Viento
                    'wind_speed': round(random.uniform(0.0, 25.0), 1),
                    'wind_direction': random.choice(wind_directions),
                    'wind_direction_degrees': random.choice([0, 45, 90, 135, 180, 225, 270, 315, 360, None]),

                    # Precipitación
                    'precipitation_3h': round(random.uniform(0.0, 15.0), 1) if random.random() > 0.7 else 0.0,
                    'precipitation_24h': round(random.uniform(0.0, 50.0), 1) if random.random() > 0.8 else 0.0,

                    # Nubes
                    'cloud_coverage': random.randint(0, 8),
                    'sky_condition': random.choice(sky_conditions),

                    # Códigos de tiempo
                    'current_weather_code': random.choice(weather_codes),
                    'current_weather_description': random.choice(weather_descriptions),
                    'past_weather1_code': random.choice(weather_codes[:10]) if random.random() > 0.3 else None,
                    'past_weather1_description': random.choice(weather_descriptions) if random.random() > 0.3 else None,
                    'past_weather2_code': random.choice(weather_codes[:10]) if random.random() > 0.5 else None,
                    'past_weather2_description': random.choice(weather_descriptions) if random.random() > 0.5 else None,

                    # Presión
                    'pressure_station': round(random.uniform(1000.0, 1025.0), 1),
                    'pressure_sea_level': round(random.uniform(1005.0, 1030.0), 1),

                    # Visibilidad
                    'visibility': round(random.uniform(5.0, 20.0), 1),

                    # Tipos de nubes
                    'cloud_low_type': random.choice(cloud_types),
                    'cloud_medium_type': random.choice(cloud_types),
                    'cloud_high_type': random.choice(cloud_types),

                    # Campos auxiliares
                    'observation_date_utc': timezone.now(),
                    'is_valid': random.choice([True, True, True, False]),  # 75% válidas
                    'validation_notes': 'Datos de prueba generados automáticamente' if random.random() > 0.8 else None,

                    # Datos crudos simulados
                    'raw_data': {
                        'source': 'test_generator',
                        'generated_at': timezone.now().isoformat(),
                        'parameters': {
                            'station_id': station.number,
                            'date': observation_date.isoformat(),
                            'hour': current_hour.strftime('%H:%M'),
                            'random_seed': random.randint(1000, 9999)
                        }
                    }
                }

                # Asegurar coherencia en los datos
                if observation_data['precipitation_3h'] > 0:
                    observation_data['cloud_coverage'] = random.randint(6, 8)
                    observation_data['relative_humidity'] = random.randint(70, 95)

                # Mostrar datos si verbose está activado
                if verbose:
                    self.stdout.write(f"\n  Observación {i + 1} para {current_hour}:")
                    self.stdout.write(f"    Temperatura: {observation_data['temperature']}°C")
                    self.stdout.write(f"    Humedad: {observation_data['relative_humidity']}%")
                    self.stdout.write(
                        f"    Viento: {observation_data['wind_speed']} km/h {observation_data['wind_direction']}")
                    self.stdout.write(f"    Precipitación 3h: {observation_data['precipitation_3h']} mm")
                    self.stdout.write(f"    Cielo: {observation_data['sky_condition']}")

                if dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [DRY RUN] Observación {i + 1}: Datos generados para {current_hour}"
                        )
                    )
                    stats['total_created'] += 1
                else:
                    try:
                        # Crear la observación
                        obj = WeatherObservation.objects.create(**observation_data)

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  Observación {i + 1}: Creada para {current_hour} (ID: {obj.id})"
                            )
                        )
                        stats['total_created'] += 1

                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  ERROR al crear observación {i + 1}: {str(e)}")
                        )

        # Mostrar resumen
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("RESUMEN DE GENERACIÓN"))
        self.stdout.write("=" * 50)
        self.stdout.write(f"Total de estaciones procesadas: {stats['total_stations']}")
        self.stdout.write(f"Total de observaciones a generar: {stats['total_observations']}")
        self.stdout.write(f"Observaciones creadas: {stats['total_created']}")
        self.stdout.write(f"Observaciones omitidas: {stats['total_skipped']}")

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    "\nMODO DRY RUN: No se guardaron datos en la base de datos"
                )
            )

        if stats['total_created'] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n¡Generación completada con éxito! {stats['total_created']} observaciones creadas."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "\nNo se crearon observaciones. Verifica las opciones."
                )
            )


class CommandError(Exception):
    pass
