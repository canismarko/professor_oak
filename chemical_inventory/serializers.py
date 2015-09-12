from rest_framework import serializers

from .models import Chemical, Container


class ChemicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chemical


class ContainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Container
