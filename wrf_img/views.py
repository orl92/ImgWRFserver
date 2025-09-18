from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .utils.plot_generators import generate_and_save_meteo_plot
import json
from django.http import JsonResponse
from django.views import View
from datetime import datetime

from .models import Simulation, MeteoImage


@method_decorator(csrf_exempt, name='dispatch')
class GeneratePlotView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            datetime_init = data.get('datetime_init')
            var_name = data.get('var_name')

            if not datetime_init or not var_name:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Se requieren datetime_init y var_name'
                }, status=400)

            # Verificar si la simulación ya existe
            simulation = Simulation.objects.filter(initial_datetime=datetime_init).first()
            if simulation:
                # Si existe, verificar si ya hay imágenes para esta variable
                existing_images = MeteoImage.objects.filter(
                    simulation=simulation,
                    variable_name=var_name
                )
                if existing_images.exists():
                    # Devolver las imágenes existentes
                    image_urls = [request.build_absolute_uri(img.image.url) for img in existing_images]
                    return JsonResponse({
                        'status': 'success',
                        'image_urls': image_urls,
                        'message': f'Ya existen {existing_images.count()} imágenes para esta simulación y variable'
                    })

            # Generar y guardar imágenes si no existen
            saved_images = generate_and_save_meteo_plot(datetime_init, var_name)
            image_urls = [request.build_absolute_uri(img.image.url) for img in saved_images]

            return JsonResponse({
                'status': 'success',
                'image_urls': image_urls,
                'message': f'Se generaron {len(saved_images)} imágenes'
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)


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
