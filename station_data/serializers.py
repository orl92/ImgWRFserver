from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from common.utils import get_img_path, get_moon_img_path, get_sun_img_path
from station_data.models import Station

class StationSerializer(serializers.ModelSerializer):
    province_code = serializers.CharField(source='province.code', read_only=True)
    province_name = serializers.CharField(source='province.name', read_only=True)

    class Meta:
        model = Station
        fields = ['province_code', 'province_name', 'name', 'number', 'latitude', 'longitude']

class StationObservationSerializer(serializers.Serializer):
    hour = serializers.CharField()
    station_number = serializers.IntegerField()
    data = serializers.JSONField()

class StationObservationAllSerializer(serializers.Serializer):
    hour = serializers.CharField()
    data = serializers.JSONField()
