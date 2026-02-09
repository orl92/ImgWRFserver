from rest_framework import serializers
from station_data.models import WeatherObservation


class WeatherObservationSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='station.name', read_only=True)
    province_name = serializers.CharField(source='station.province.name', read_only=True, allow_null=True)
    # town_name = serializers.CharField(source='station.town.name', read_only=True, allow_null=True)

    class Meta:
        model = WeatherObservation
        fields = [
            # Identificadores
            'station_number',

            # Información de estación
            'station_name', 'province_name',

            # Fecha y hora
            'date', 'hour',

            # Datos meteorológicos principales
            'temperature', 'max_temperature', 'min_temperature',
            'relative_humidity', 'wind_speed', 'wind_direction',
            'wind_direction_degrees', 'precipitation_3h', 'precipitation_24h',
            'cloud_coverage', 'sky_condition',

            # Tiempo presente y pasado
            'current_weather_code', 'current_weather_description',
            'past_weather1_code', 'past_weather1_description',
            'past_weather2_code', 'past_weather2_description',

            # Campos adicionales SYNOP
            'pressure_station', 'pressure_sea_level', 'dew_point',
            'visibility', 'cloud_low_type', 'cloud_medium_type', 'cloud_high_type',

            # Campos auxiliares
            'raw_data', 'is_valid', 'validation_notes'
        ]
        read_only_fields = fields