from rest_framework import serializers

from .models import Chemical, Container, Glove, Supplier

class GloveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Glove


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier


class ChemicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chemical


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
