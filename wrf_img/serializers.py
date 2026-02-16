from rest_framework import serializers
from .models import Simulation, MeteoImage

class SimulationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Simulation
        fields = ['initial_datetime']  # o los campos que necesites

class MeteoImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = MeteoImage
        fields = ['variable_name', 'valid_datetime', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url
