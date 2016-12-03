import json

from rest_framework import serializers

from .models import Chemical, Hazard, Container, Glove, Supplier

class GloveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Glove
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class ChemicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chemical
        fields = "__all__"


class HazardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hazard
        fields = "__all__"


class ContainerSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        """Remove time part of datetime strings passed by javascript."""
        def fix_date(field_key):
            if field_key in data.keys():
                oldString = data[field_key]
                data[field_key] = oldString[0:10]
        for field in ['date_opened', 'expiration_date']:
            fix_date(field)
        validated_data = super().to_internal_value(data)
        return validated_data

    class Meta:
        model = Container
        fields = "__all__"
