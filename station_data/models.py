# models.py
from django.db import models
import uuid


# Create your models here.
class Province(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=15, verbose_name='Nombre')
    code = models.CharField(max_length=5, unique=True, verbose_name='Código')

    class Meta:
        verbose_name = 'Provincia'
        verbose_name_plural = "Provincias"
        default_permissions = ()
        permissions = (
            ('view_province', 'Ver'),
            ('add_province', 'Añadir'),
            ('change_province', 'Editar'),
            ('delete_province', 'Eliminar'),
        )

    def __str__(self):
        return self.name


class Town(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, related_name="towns",
                                 verbose_name='Provincia')
    name = models.CharField(max_length=25, verbose_name='Nombre')
    latitude = models.FloatField(verbose_name='Latitud')
    longitude = models.FloatField(verbose_name='Longitud')

    class Meta:
        verbose_name = 'Municipio'
        verbose_name_plural = "Municipios"
        default_permissions = ()
        permissions = (
            ('view_town', 'Ver'),
            ('add_town', 'Añadir'),
            ('change_town', 'Editar'),
            ('delete_town', 'Eliminar'),
        )

    def __str__(self):
        return self.name


class Station(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, related_name="stations",
                                 verbose_name='Provincia')
    town = models.ForeignKey(Town, on_delete=models.SET_NULL, null=True, blank=True, related_name="stations",
                             verbose_name='Municipio')
    name = models.CharField(max_length=50, verbose_name='Nombre')
    number = models.IntegerField(unique=True, verbose_name='Número de estación')
    latitude = models.FloatField(verbose_name='Latitud')
    longitude = models.FloatField(verbose_name='Longitud')
    altitude = models.FloatField(null=True, blank=True, verbose_name='Altitud (m)')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    station_type = models.CharField(
        max_length=20,
        choices=[
            ('synoptic', 'Sinóptica'),
            ('climatic', 'Climática'),
            ('automatic', 'Automática'),
            ('agrometeorological', 'Agrometeorológica'),
        ],
        default='synoptic',
        verbose_name='Tipo de estación'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')

    class Meta:
        verbose_name = 'Estación'
        verbose_name_plural = "Estaciones"
        default_permissions = ()
        permissions = (
            ('view_station', 'Ver'),
            ('add_station', 'Añadir'),
            ('change_station', 'Editar'),
            ('delete_station', 'Eliminar'),
        )
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['province', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.number})"

    @property
    def full_name(self):
        """Nombre completo de la estación con provincia"""
        if self.province:
            return f"{self.name} - {self.province.name}"
        return self.name


class WeatherObservation(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="observations",
        verbose_name='Estación'
    )
    station_number = models.IntegerField(verbose_name='Número de estación', db_index=True)
    date = models.DateField(verbose_name='Fecha')
    hour = models.TimeField(verbose_name='Hora')

    # Datos meteorológicos principales
    temperature = models.FloatField(null=True, blank=True, verbose_name='Temperatura (°C)')
    max_temperature = models.FloatField(null=True, blank=True, verbose_name='Temperatura máxima (°C)')
    min_temperature = models.FloatField(null=True, blank=True, verbose_name='Temperatura mínima (°C)')
    relative_humidity = models.FloatField(null=True, blank=True, verbose_name='Humedad relativa (%)')
    wind_speed = models.FloatField(null=True, blank=True, verbose_name='Velocidad del viento (Km/h)')
    wind_direction = models.CharField(max_length=20, null=True, blank=True, verbose_name='Dirección del viento')
    wind_direction_degrees = models.IntegerField(null=True, blank=True, verbose_name='Dirección (grados)')
    precipitation_3h = models.FloatField(null=True, blank=True, verbose_name='Precipitación 3h (mm)')
    precipitation_24h = models.FloatField(null=True, blank=True, verbose_name='Precipitación 24h (mm)')
    cloud_coverage = models.IntegerField(null=True, blank=True, verbose_name='Cielo cubierto (octavos)')
    sky_condition = models.CharField(max_length=50, null=True, blank=True, verbose_name='Estado del cielo')

    # Nuevos campos para tiempo presente y pasado
    current_weather_code = models.CharField(max_length=2, null=True, blank=True, verbose_name='Código tiempo presente')
    current_weather_description = models.TextField(null=True, blank=True, verbose_name='Descripción tiempo presente')
    past_weather1_code = models.CharField(max_length=1, null=True, blank=True, verbose_name='Código tiempo pasado 1')
    past_weather1_description = models.TextField(null=True, blank=True, verbose_name='Descripción tiempo pasado 1')
    past_weather2_code = models.CharField(max_length=1, null=True, blank=True, verbose_name='Código tiempo pasado 2')
    past_weather2_description = models.TextField(null=True, blank=True, verbose_name='Descripción tiempo pasado 2')

    # Campos adicionales del SYNOP
    pressure_station = models.FloatField(null=True, blank=True, verbose_name='Presión estación (hPa)')
    pressure_sea_level = models.FloatField(null=True, blank=True, verbose_name='Presión nivel mar (hPa)')
    dew_point = models.FloatField(null=True, blank=True, verbose_name='Punto de rocío (°C)')
    visibility = models.FloatField(null=True, blank=True, verbose_name='Visibilidad (km)')
    cloud_low_type = models.CharField(max_length=2, null=True, blank=True, verbose_name='Tipo nubes bajas')
    cloud_medium_type = models.CharField(max_length=2, null=True, blank=True, verbose_name='Tipo nubes medias')
    cloud_high_type = models.CharField(max_length=2, null=True, blank=True, verbose_name='Tipo nubes altas')

    # Campos auxiliares
    observation_date_utc = models.DateTimeField(null=True, blank=True, verbose_name='Fecha observación UTC')
    downloaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Descargado el')
    raw_data = models.JSONField(null=True, blank=True, verbose_name='Datos crudos')
    is_valid = models.BooleanField(default=True, verbose_name='Válido')
    validation_notes = models.TextField(null=True, blank=True, verbose_name='Notas de validación')

    class Meta:
        verbose_name = 'Observación meteorológica'
        verbose_name_plural = "Observaciones meteorológicas"
        default_permissions = ()
        permissions = (
            ('view_weatherobservation', 'Ver'),
            ('add_weatherobservation', 'Añadir'),
            ('change_weatherobservation', 'Editar'),
            ('delete_weatherobservation', 'Eliminar'),
        )
        unique_together = ['station', 'date', 'hour']
        indexes = [
            models.Index(fields=['station', 'date']),
            models.Index(fields=['date', 'hour']),
            models.Index(fields=['station_number', 'date']),
            models.Index(fields=['downloaded_at']),
        ]
        ordering = ['-date', '-hour', 'station']

    def __str__(self):
        return f"{self.station.name if self.station else 'Estación ' + str(self.station_number)} - {self.date} {self.hour}"

    def save(self, *args, **kwargs):
        # Asegurar que station_number esté sincronizado con station.number
        if self.station and not self.station_number:
            self.station_number = self.station.number
        elif self.station_number and not self.station:
            # Intentar encontrar la estación por número
            try:
                self.station = Station.objects.get(number=self.station_number)
            except Station.DoesNotExist:
                pass

        super().save(*args, **kwargs)

    @property
    def station_name(self):
        """Nombre de la estación"""
        if self.station:
            return self.station.name
        return f"Estación {self.station_number}"

    @property
    def province_name(self):
        """Nombre de la provincia"""
        if self.station and self.station.province:
            return self.station.province.name
        return None

    @property
    def town_name(self):
        """Nombre del municipio"""
        if self.station and self.station.town:
            return self.station.town.name
        return None


class StationDataStatus(models.Model):
    """Modelo para rastrear el estado de descarga de datos por estación y fecha"""
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        related_name="data_status",
        verbose_name='Estación'
    )
    date = models.DateField(verbose_name='Fecha')
    hour = models.TimeField(verbose_name='Hora')

    # Estados de descarga
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('downloading', 'Descargando'),
        ('downloaded', 'Descargado'),
        ('processed', 'Procesado'),
        ('error', 'Error'),
        ('not_found', 'No encontrado'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )

    # Información de error
    error_message = models.TextField(null=True, blank=True, verbose_name='Mensaje de error')
    retry_count = models.IntegerField(default=0, verbose_name='Intentos')

    # Tiempos
    last_download_attempt = models.DateTimeField(null=True, blank=True, verbose_name='Último intento')
    downloaded_at = models.DateTimeField(null=True, blank=True, verbose_name='Descargado el')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='Procesado el')

    # Metadatos
    file_size = models.IntegerField(null=True, blank=True, verbose_name='Tamaño archivo (bytes)')
    raw_filename = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nombre archivo')

    class Meta:
        verbose_name = 'Estado de datos de estación'
        verbose_name_plural = "Estados de datos de estación"
        unique_together = ['station', 'date', 'hour']
        indexes = [
            models.Index(fields=['station', 'date']),
            models.Index(fields=['status', 'date']),
        ]
        ordering = ['-date', '-hour', 'station']

    def __str__(self):
        return f"{self.station.name} - {self.date} {self.hour} - {self.get_status_display()}"