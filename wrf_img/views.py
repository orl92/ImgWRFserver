from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Simulation, MeteoImage
from .serializers import SimulationSerializer, MeteoImageSerializer


class SimulationListView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SimulationSerializer  # Se usa cuando no hay filtros

    def get_queryset(self):
        return Simulation.objects.all().order_by('-initial_datetime')

    def get(self, request):
        datetime_init = request.GET.get('datetime_init')
        var_name = request.GET.get('var_name')

        # Caso con filtros: devolver imágenes
        if datetime_init and var_name:
            try:
                # Convertir a datetime (asumiendo formato YYYYMMDDHH)
                from datetime import datetime
                dt_obj = datetime.strptime(datetime_init, '%Y%m%d%H')
                simulation = Simulation.objects.filter(initial_datetime=dt_obj).first()

                if not simulation:
                    return Response({
                        'status': 'error',
                        'message': f'No se encontró simulación para la fecha: {datetime_init}'
                    }, status=status.HTTP_404_NOT_FOUND)

                images = MeteoImage.objects.filter(
                    simulation=simulation,
                    variable_name=var_name
                ).order_by('valid_datetime')

                if not images.exists():
                    return Response({
                        'status': 'error',
                        'message': f'No se encontraron imágenes para la variable: {var_name}'
                    }, status=status.HTTP_404_NOT_FOUND)

                # Serializar imágenes pasando el request para construir URLs absolutas
                serializer = MeteoImageSerializer(images, many=True, context={'request': request})
                return Response({
                    'status': 'success',
                    'simulation_date': simulation.initial_datetime.isoformat(),
                    'variable_name': var_name,
                    'image_urls': [item['image_url'] for item in serializer.data],
                    'count': len(serializer.data)
                })

            except ValueError:
                return Response({
                    'status': 'error',
                    'message': 'Formato de fecha inválido. Use YYYYMMDDHH'
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Sin filtros: devolver lista de simulaciones
        else:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'simulations': [item['initial_datetime'] for item in serializer.data],
                'count': len(serializer.data)
            })
