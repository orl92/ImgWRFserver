from django.contrib import admin
from django.utils.html import format_html
from .models import Simulation, MeteoImage


@admin.register(Simulation)
class SimulationAdmin(admin.ModelAdmin):
    list_display = ('initial_datetime', 'created_at', 'image_count', 'variables_available')
    list_filter = ('initial_datetime', 'created_at')
    search_fields = ('initial_datetime', 'description')
    readonly_fields = ('created_at', 'image_count', 'variables_available')

    def image_count(self, obj):
        return obj.image_count()

    image_count.short_description = 'Nº de Imágenes'

    def variables_available(self, obj):
        return ", ".join(obj.variables_available())

    variables_available.short_description = 'Variables Disponibles'


@admin.register(MeteoImage)
class MeteoImageAdmin(admin.ModelAdmin):
    list_display = ('variable_name', 'simulation', 'valid_datetime', 'image_preview', 'created_at')
    list_filter = ('variable_name', 'simulation__initial_datetime', 'valid_datetime', 'created_at')
    search_fields = ('variable_name', 'simulation__initial_datetime')
    readonly_fields = ('image_preview', 'data_min', 'data_max', 'data_mean', 'created_at')
    fieldsets = (
        ('Relación', {
            'fields': ('simulation',)
        }),
        ('Información Temporal', {
            'fields': ('valid_datetime',)
        }),
        ('Datos Meteorológicos', {
            'fields': ('variable_name', 'data_min', 'data_max', 'data_mean')
        }),
        ('Imagen', {
            'fields': ('image', 'image_preview', 'created_at')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="150" height="100" style="object-fit: cover;" />', obj.image.url)
        return "No hay imagen"

    image_preview.short_description = 'Vista Previa'