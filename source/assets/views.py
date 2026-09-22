from rest_framework import viewsets, permissions
from .models import CompanyAsset
from .serializers import CompanyAssetSerializer

class CompanyAssetViewSet(viewsets.ModelViewSet):
    queryset = CompanyAsset.objects.all()
    serializer_class = CompanyAssetSerializer
    permission_classes = [permissions.IsAuthenticated]