from rest_framework import serializers

from .models import Chemical


class ChemicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chemical
