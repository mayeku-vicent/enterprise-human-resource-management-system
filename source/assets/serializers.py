from rest_framework import serializers
from .models import CompanyAsset

class CompanyAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyAsset
        fields = '__all__'