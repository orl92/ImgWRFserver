from django.urls import path
from station_data.views import StationsDataAPIView

urlpatterns = [
    path('stations_data/', StationsDataAPIView.as_view(), name='stations_data'),
]