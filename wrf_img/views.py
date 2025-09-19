from django.http import JsonResponse
from django.views import View
from datetime import datetime

from .models import Simulation, MeteoImage


class SimulationListView(View):
    def get(self, request):
        # Verificar si se han proporcionado parámetros de filtrado
        datetime_init = request.GET.get('datetime_init')
        var_name = request.GET.get('var_name')

        # Si se proporcionan ambos parámetros, buscar imágenes específicas
        if datetime_init and var_name:
            try:
                # Convertir el formato YYYYMMDDHH a datetime
                dt_obj = datetime.strptime(datetime_init, '%Y%m%d%H')

                # Buscar la simulación
                simulation = Simulation.objects.filter(initial_datetime=dt_obj).first()

                if not simulation:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'No se encontró simulación para la fecha: {datetime_init}'
                    }, status=404)

                # Buscar las imágenes para esta simulación y variable
                images = MeteoImage.objects.filter(
                    simulation=simulation,
                    variable_name=var_name
                ).order_by('valid_datetime')

                if not images.exists():
                    return JsonResponse({
                        'status': 'error',
                        'message': f'No se encontraron imágenes para la variable: {var_name}'
                    }, status=404)

                # Construir URLs de las imágenes
                image_urls = [request.build_absolute_uri(img.image.url) for img in images]

                return JsonResponse({
                    'status': 'success',
                    'simulation_date': simulation.initial_datetime.isoformat(),
                    'variable_name': var_name,
                    'image_urls': image_urls,
                    'count': len(image_urls)
                })

            except ValueError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Formato de fecha inválido. Use YYYYMMDDHH'
                }, status=400)
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=500)

        # Si no se proporcionan parámetros, devolver todas las simulaciones
        else:
            simulations = Simulation.objects.all().order_by('-initial_datetime')

            # Crear lista de fechas en formato ISO
            simulation_dates = [
                sim.initial_datetime.isoformat()
                for sim in simulations
            ]

            return JsonResponse({
                'status': 'success',
                'simulations': simulation_dates,
                'count': len(simulation_dates)
            })
