from django.contrib import admin
from django.utils.html import format_html
from .models import Province, Town, Station


@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    list_filter = ('name', 'code')
    search_fields = ('name', 'code')
    readonly_fields = ('name', 'code')

@admin.register(Town)
class TownAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')

@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'latitude', 'longitude')
    list_filter = ('name', 'number',)
    search_fields = ('name', 'number',)
    readonly_fields = ('name', 'number',)