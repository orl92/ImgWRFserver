# admin.py
from django.contrib import admin
from .models import Province, Town, Station, WeatherObservation, StationDataStatus


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'uuid')
    search_fields = ('name', 'code')
    ordering = ('name',)
    readonly_fields = ('uuid',)


@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'latitude', 'longitude')
    list_filter = ('province',)
    search_fields = ('name', 'province__name')
    raw_id_fields = ('province',)
    readonly_fields = ('uuid',)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'province', 'town', 'station_type', 'is_active')
    list_filter = ('province', 'station_type', 'is_active')
    search_fields = ('name', 'number', 'province__name', 'town__name')
    raw_id_fields = ('province', 'town')
    readonly_fields = ('uuid', 'created_at', 'updated_at')
    list_per_page = 20

    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'number', 'province', 'town')
        }),
        ('Ubicación', {
            'fields': ('latitude', 'longitude', 'altitude')
        }),
        ('Configuración', {
            'fields': ('station_type', 'is_active')
        }),
        ('Metadatos', {
            'fields': ('uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class StationNumberFilter(admin.SimpleListFilter):
    title = 'estación'
    parameter_name = 'station_number'

    def lookups(self, request, model_admin):
        # Obtener números de estación únicos con sus nombres
        stations = Station.objects.filter(is_active=True).values_list('number', 'name').distinct()[:50]
        return [(str(num), f"{num} - {name}") for num, name in stations]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(station_number=self.value())
        return queryset


@admin.register(WeatherObservation)
class WeatherObservationAdmin(admin.ModelAdmin):
    list_display = ('station_name', 'date', 'hour', 'temperature', 'relative_humidity', 'precipitation_24h', 'is_valid')
    list_filter = (StationNumberFilter, 'date', 'is_valid')
    search_fields = ('station__name', 'station_number', 'date')
    raw_id_fields = ('station',)
    readonly_fields = ('uuid', 'downloaded_at', 'station_name', 'province_name', 'town_name')
    date_hierarchy = 'date'
    list_per_page = 50

    fieldsets = (
        ('Información Básica', {
            'fields': ('station', 'station_number', 'date', 'hour')
        }),
        ('Datos Meteorológicos', {
            'fields': (
                'temperature', 'max_temperature', 'min_temperature',
                'relative_humidity', 'dew_point'
            )
        }),
        ('Viento', {
            'fields': ('wind_speed', 'wind_direction', 'wind_direction_degrees')
        }),
        ('Precipitación', {
            'fields': ('precipitation_3h', 'precipitation_24h')
        }),
        ('Cielo y Nubes', {
            'fields': (
                'cloud_coverage', 'sky_condition',
                'cloud_low_type', 'cloud_medium_type', 'cloud_high_type'
            )
        }),
        ('Tiempo Presente y Pasado', {
            'fields': (
                'current_weather_code', 'current_weather_description',
                'past_weather1_code', 'past_weather1_description',
                'past_weather2_code', 'past_weather2_description'
            ),
            'classes': ('collapse',)
        }),
        ('Presión y Visibilidad', {
            'fields': ('pressure_station', 'pressure_sea_level', 'visibility'),
            'classes': ('collapse',)
        }),
        ('Metadatos y Validación', {
            'fields': (
                'observation_date_utc', 'downloaded_at',
                'is_valid', 'validation_notes', 'raw_data'
            ),
            'classes': ('collapse',)
        }),
        ('Campos Calculados (solo lectura)', {
            'fields': ('station_name', 'province_name', 'town_name'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StationDataStatus)
class StationDataStatusAdmin(admin.ModelAdmin):
    list_display = ('station', 'date', 'hour', 'status', 'retry_count', 'last_download_attempt')
    list_filter = ('status', 'station', 'date')
    search_fields = ('station__name', 'station__number', 'error_message')
    raw_id_fields = ('station',)
    readonly_fields = ('uuid', 'last_download_attempt', 'downloaded_at', 'processed_at')
    list_per_page = 50

    fieldsets = (
        ('Información Básica', {
            'fields': ('station', 'date', 'hour')
        }),
        ('Estado de Descarga', {
            'fields': ('status', 'retry_count', 'error_message')
        }),
        ('Tiempos', {
            'fields': ('last_download_attempt', 'downloaded_at', 'processed_at')
        }),
        ('Metadatos del Archivo', {
            'fields': ('file_size', 'raw_filename'),
            'classes': ('collapse',)
        }),
    )