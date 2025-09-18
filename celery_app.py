import os
from celery import Celery
from celery.schedules import crontab

# Establecer la configuración de Django por defecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'congf.settings')

app = Celery('meteo_server')

# Usar la configuración de Django para Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar tareas desde todas las aplicaciones Django registradas
app.autodiscover_tasks()

# Configurar tareas periódicas
app.conf.beat_schedule = {
    'generate-meteo-images-4am': {
        'task': 'wrf_img.tasks.generate_meteo_images_task',  # Cambiado de meteo_images a wrf_img
        'schedule': crontab(hour=4, minute=0),
        'args': (4,),
    },
    'generate-meteo-images-10am': {
        'task': 'wrf_img.tasks.generate_meteo_images_task',  # Cambiado de meteo_images a wrf_img
        'schedule': crontab(hour=10, minute=0),
        'args': (10,),
    },
    'generate-meteo-images-4pm': {
        'task': 'wrf_img.tasks.generate_meteo_images_task',  # Cambiado de meteo_images a wrf_img
        'schedule': crontab(hour=16, minute=0),
        'args': (16,),
    },
    'generate-meteo-images-10pm': {
        'task': 'wrf_img.tasks.generate_meteo_images_task',  # Cambiado de meteo_images a wrf_img
        'schedule': crontab(hour=22, minute=0),
        'args': (22,),
    },
}