from django.urls import path
from . import views

urlpatterns = [
    path('simulations/', views.SimulationListView.as_view(), name='simulation_list'),  # Única ruta para ambas funcionalidades
]
