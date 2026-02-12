from django.urls import path
from station_data.views import StationsDataAPIView

urlpatterns = [
    path('', StationsDataAPIView.as_view(), name='stations_data'),
]