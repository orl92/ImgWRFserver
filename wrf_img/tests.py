import os
import django
from django.test import TestCase
from django.core.management import call_command

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'congf.settings')
django.setup()


class MeteoImageGenerationTest(TestCase):
    def test_image_generation(self):
        """Test que genera imágenes para todas las variables"""
        # Llama al comando de gestión
        try:
            call_command('generate_meteo_images')
            self.assertTrue(True, "Comando ejecutado exitosamente")
        except Exception as e:
            self.fail(f"Error ejecutando el comando: {str(e)}")
