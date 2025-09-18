from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from .utils.plot_generators import generate_and_save_meteo_plot
from .models import Simulation
import logging

logger = logging.getLogger(__name__)


@shared_task
def generate_meteo_images_task(hour):
    """
    Tarea para generar imágenes meteorológicas en horarios específicos
    """
    try:
        # Calcular la fecha y hora inicial para la API
        now = timezone.now()

        # Determinar el ciclo según la hora de ejecución
        if hour == 4:
            cycle_hour = 0  # 00Z
        elif hour == 10:
            cycle_hour = 6  # 06Z
        elif hour == 16:
            cycle_hour = 12  # 12Z
        elif hour == 22:
            cycle_hour = 18  # 18Z
        else:
            cycle_hour = 0  # Por defecto

        # Ajustar la fecha según el ciclo
        if now.hour < cycle_hour:
            # Si la hora actual es anterior al ciclo, usar el día anterior
            initial_datetime = now.replace(hour=cycle_hour, minute=0, second=0, microsecond=0) - timedelta(days=1)
        else:
            # Usar el día actual
            initial_datetime = now.replace(hour=cycle_hour, minute=0, second=0, microsecond=0)

        # Formatear para la función (formato completo)
        datetime_init_str = initial_datetime.strftime('%Y-%m-%d %H:%M:%S')

        # Lista de variables a generar
        variables = ['T2', 'rh2', 'RAINC', 'slp', 'ws10', 'wd10']

        # Verificar si ya existe una simulación para esta fecha
        # Usar datetime consciente de zona horaria para la búsqueda
        simulation_exists = Simulation.objects.filter(initial_datetime=initial_datetime).exists()

        if simulation_exists:
            logger.info(f"Simulación para {datetime_init_str} ya existe. Saltando generación.")
            return f"Simulación para {datetime_init_str} ya existe"

        # Generar imágenes para cada variable
        results = {}
        for var_name in variables:
            try:
                saved_images = generate_and_save_meteo_plot(datetime_init_str, var_name)
                results[var_name] = f"Generadas {len(saved_images)} imágenes"
                logger.info(f"Generadas {len(saved_images)} imágenes para {var_name}")
            except Exception as e:
                results[var_name] = f"Error: {str(e)}"
                logger.error(f"Error generando imágenes para {var_name}: {str(e)}")

        return {
            'initial_datetime': datetime_init_str,
            'results': results,
            'generated_at': now.isoformat()
        }

    except Exception as e:
        logger.error(f"Error en la tarea de generación de imágenes: {str(e)}")
        return {'error': str(e)}
