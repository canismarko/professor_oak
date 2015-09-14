from rest_framework import serializers

from .models import Chemical, Container


class ChemicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chemical


class ContainerSerializer(serializers.ModelSerializer):

    def to_internal_value(self, data):
        """Remove time part of datetime strings passed by javascript."""
        def fix_date(field_key):
            oldString = data[field_key]
            data[field_key] = oldString[0:10]
        for field in ['date_opened', 'expiration_date']:
            fix_date(field)
        print(data)
        validated_data = super().to_internal_value(data)
        return validated_data

    class Meta:
        model = Container
