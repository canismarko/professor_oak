from rest_framework import serializers

from .models import stock_take

class StockSerializer(serializers.ModelSerializer):
	class Meta:
		model = stock_take
