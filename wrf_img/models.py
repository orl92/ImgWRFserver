from django.db import models
from django.utils import timezone
import os
from django.db.models.signals import post_delete
from django.dispatch import receiver


class Simulation(models.Model):
    """Modelo que representa una simulación meteorológica con una fecha inicial específica"""
    initial_datetime = models.DateTimeField(
        unique=True,
        help_text="Fecha y hora inicial de la simulación (con zona horaria)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True, help_text="Descripción opcional de la simulación")

    class Meta:
        ordering = ['-initial_datetime']
        verbose_name = 'Simulación'
        verbose_name_plural = 'Simulaciones'

    def __str__(self):
        return f"Simulación {self.initial_datetime}"

    def image_count(self):
        """Retorna el número de imágenes asociadas a esta simulación"""
        return self.meteoimage_set.count()

    def variables_available(self):
        """Retorna las variables disponibles para esta simulación"""
        return self.meteoimage_set.values_list('variable_name', flat=True).distinct()


class MeteoImage(models.Model):
    """Modelo que representa una imagen meteorológica generada a partir de una simulación"""

    def get_upload_path(self, filename):
        """
        Genera la ruta: meteo_plots/[datetime simulacion]/[nombre variable]/[filename]
        """
        simulation_time = self.simulation.initial_datetime.strftime("%Y%m%d_%H%M%S")
        return os.path.join('meteo_plots', simulation_time, self.variable_name, filename)

    simulation = models.ForeignKey(
        Simulation,
        on_delete=models.CASCADE,
        help_text="Simulación a la que pertenece esta imagen"
    )
    valid_datetime = models.DateTimeField(help_text="Fecha y hora válida de la imagen (con zona horaria)")
    variable_name = models.CharField(max_length=20, help_text="Nombre de la variable meteorológica")
    image = models.ImageField(upload_to=get_upload_path, help_text="Imagen generada")
    created_at = models.DateTimeField(auto_now_add=True)

    # Información adicional sobre los datos
    data_min = models.FloatField(null=True, blank=True)
    data_max = models.FloatField(null=True, blank=True)
    data_mean = models.FloatField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['simulation', 'variable_name']),
            models.Index(fields=['valid_datetime']),
        ]
        unique_together = ['simulation', 'valid_datetime', 'variable_name']
        ordering = ['simulation', 'valid_datetime', 'variable_name']

    def __str__(self):
        return f"{self.variable_name} - {self.valid_datetime} (Sim: {self.simulation.initial_datetime})"


# Señal para eliminar archivos de imagen cuando se borre la instancia
@receiver(post_delete, sender=MeteoImage)
def delete_meteroimage_file(sender, instance, **kwargs):
    """
    Elimina el archivo de imagen cuando se borra una instancia de MeteoImage
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)