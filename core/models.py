import os
import uuid

from django.conf import settings
from django.db import models


def generic_image_path(instance, filename):
    """
    Genera una ruta única para imágenes.
    Ejemplo: img/imagemodel/123e4567-e89b-12d3-a456-426614174000.png
    """
    random_filename = str(uuid.uuid4())
    extension = os.path.splitext(filename)[1]
    return 'img/{}/{}{}'.format(
        instance.__class__.__name__.lower(),
        random_filename,
        extension
    )

def generic_pdf_path(instance, filename):
    """
    Genera una ruta única para archivos PDF.
    """
    random_filename = str(uuid.uuid4())
    extension = os.path.splitext(filename)[1]
    return 'pdf/{}/{}{}'.format(
        instance.__class__.__name__.lower(),
        random_filename,
        extension
    )

class ImageModel(models.Model):
    """
    Modelo abstracto que maneja automáticamente la eliminación de archivos
    cuando se actualiza o elimina la imagen.
    """
    image = models.ImageField(upload_to=generic_image_path, verbose_name='Imagen')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Eliminar archivo anterior si se reemplaza la imagen
        try:
            this = self.__class__.objects.get(id=self.id)
            if this.image and this.image != self.image:
                this.image.delete(save=False)
        except self.__class__.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Eliminar archivo al borrar el registro
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

    def get_image(self):
        """Devuelve la URL de la imagen o un placeholder por defecto."""
        if self.image:
            return f'{settings.MEDIA_URL}{self.image}'
        return f'{settings.STATIC_URL}dist/img/default.svg'
  