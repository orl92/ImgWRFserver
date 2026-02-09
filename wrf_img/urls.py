from django.urls import path
from . import views

urlpatterns = [
    path('simulations/', views.SimulationListView.as_view(), name='simulation_list'),  # Única ruta para ambas funcionalidades Ej:http://localhost:8000/simulations/?datetime_init=2026020400&var_name=T2
]
