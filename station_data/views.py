from datetime import datetime
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from station_data.models import WeatherObservation
from station_data.serializers import WeatherObservationSerializer


class StationsDataAPIView(APIView):
    """
    API para datos de observaciones meteorológicas
    URL: /stations_data/?date=YYYYMMDD&time=HH&station=NNNNN
    """
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Obtener parámetros de la URL
            date_param = request.query_params.get('date')
            time_param = request.query_params.get('time')
            station_param = request.query_params.get('station')

            # Comenzar con todas las observaciones
            queryset = WeatherObservation.objects.all()

            # Filtrar por fecha si se proporciona
            if date_param:
                date_obj = datetime.strptime(date_param, '%Y%m%d').date()
                queryset = queryset.filter(date=date_obj)

            # Filtrar por hora si se proporciona (en UTC)
            if time_param:
                time_str = str(time_param).zfill(2)
                time_obj = datetime.strptime(time_str, '%H').time()
                queryset = queryset.filter(hour=time_obj)

            # Filtrar por estación si se proporciona
            if station_param:
                station_number = int(station_param)
                queryset = queryset.filter(station_number=station_number)

            # Ordenar según el Meta del modelo
            queryset = queryset.order_by('-date', '-hour', 'station')

            # Serializar TODOS los datos del modelo
            serializer = WeatherObservationSerializer(queryset, many=True)

            # Respuesta exitosa
            return Response({
                "status": "success",
                "count": queryset.count(),
                "date_filter": date_param,
                "time_filter": time_param,
                "station_filter": station_param,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            # Error en formato de parámetros
            return Response({
                "status": "error",
                "message": "Parámetro inválido",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Error general
            return Response({
                "status": "error",
                "message": "Error interno del servidor",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)