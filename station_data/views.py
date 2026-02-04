from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from station_data.data.GetData import GetData
from station_data.serializers import (StationObservationSerializer,
                                      StationSerializer)
from station_data.models import Station

# Create your views here.
    
class StationObservationView(GenericAPIView):
    """
    ### Vista de Observación de Estación Meteorológica
    Recupera datos de observación para una estación específica a una hora determinada.

    **Parámetros:**
    - `hour` (str): Hora de observación (formato HH). 
      Horas permitidas: 00, 03, 06, 09, 12, 15, 18, 21
    - `station_number` (str): Número de la estación meteorológica.
    
    **Estaciones disponibles:**
    - Florida: 78350
    - Palo Seco: 78354
    - Nuevitas: 78353
    - Esmeralda: 78352
    - Santa Cruz: 78351
    - Camagüey: 78355
    
    **Respuestas:**
    - `200 OK`: Devuelve los datos de observación.
    - `400 Bad Request`: Devuelve errores de validación.
    """
    permission_classes = [AllowAny]
    serializer_class = StationObservationSerializer

    def get(self, request, hour, station_number):
        allowed_hours = {'00', '03', '06', '09', '12', '15', '18', '21'}
        stations = {
            '78350': 'Florida',
            '78354': 'Palo Seco',
            '78353': 'Nuevitas',
            '78352': 'Esmeralda',
            '78351': 'Santa Cruz',
            '78355': 'Camagüey'
        }
        
        hour_str = str(hour).zfill(2)
        
        if hour_str not in allowed_hours:
            return Response(
                {"error": "Invalid hour parameter. Valid hours: 00, 03, 06, 09, 12, 15, 18, 21"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if str(station_number) not in stations:
            return Response(
                {"error": "Invalid station number. Available stations: " + ", ".join(f"{k} ({v})" for k, v in stations.items())},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = GetData().get_station(hour_str, station_number)
        serializer = self.get_serializer(data={'hour': hour_str, 'station_number': station_number, 'data': data})
        
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class StationListAPIView(ListAPIView):
    """
    ### Vista de Listado de Estaciones
    Esta vista proporciona una lista de todas las estaciones.
    
    **Respuestas:**
    - `200 OK`: Devuelve la lista de estaciones.
    """
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [AllowAny]

    


