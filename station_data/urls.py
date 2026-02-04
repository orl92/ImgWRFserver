from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.routers import DefaultRouter

from station_data.views import (StationListAPIView,
                                StationObservationView)

router = DefaultRouter()

urlpatterns = router.urls + [
    # Autenticacion
    path('auth/', include('rest_framework.urls')),
    # Documentacion
    path('doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='doc'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Estaciones
    path('stations/', StationListAPIView.as_view(), name='station-list'),
    path('station/observation/<str:hour>/<int:station_number>/', StationObservationView.as_view(), name='station-observation'),
]