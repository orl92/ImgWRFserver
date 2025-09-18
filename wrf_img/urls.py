from django.urls import path
from . import views

urlpatterns = [
    path('generate-plot/', views.GeneratePlotView.as_view(), name='generate_plot'),
    path('simulations/', views.SimulationListView.as_view(), name='simulation_list'),  # Única ruta para ambas funcionalidades
]
