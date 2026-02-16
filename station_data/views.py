from datetime import datetime

from drf_spectacular.utils import OpenApiParameter
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from station_data.models import WeatherObservation
from station_data.serializers import WeatherObservationSerializer

from datetime import datetime
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from station_data.models import WeatherObservation
from station_data.serializers import WeatherObservationSerializer

class StationsDataAPIView(GenericAPIView):
    """
    API para datos de observaciones meteorológicas
    URL: /stations_data/?date=YYYYMMDD&time=HH&station=NNNNN
    """
    permission_classes = [AllowAny]
    serializer_class = WeatherObservationSerializer
    queryset = WeatherObservation.objects.all()

    def get_queryset(self):
        """
        Aplica los filtros de los parámetros de consulta.
        """
        queryset = super().get_queryset()
        request = self.request

        date_param = request.query_params.get('date')
        time_param = request.query_params.get('time')
        station_param = request.query_params.get('station')

        if date_param:
            date_obj = datetime.strptime(date_param, '%Y%m%d').date()
            queryset = queryset.filter(date=date_obj)

        if time_param:
            time_str = str(time_param).zfill(2)
            time_obj = datetime.strptime(time_str, '%H').time()
            queryset = queryset.filter(hour=time_obj)

        if station_param:
            station_number = int(station_param)
            queryset = queryset.filter(station_number=station_number)

        # Ordenar según el Meta del modelo
        return queryset.order_by('-date', '-hour', 'station')

    def get(self, request):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            return Response({
                "status": "success",
                "count": queryset.count(),
                "date_filter": request.query_params.get('date'),
                "time_filter": request.query_params.get('time'),
                "station_filter": request.query_params.get('station'),
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({
                "status": "error",
                "message": "Parámetro inválido",
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": "error",
                "message": "Error interno del servidor",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
