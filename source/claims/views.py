from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ExpenseClaim
from .serializers import ExpenseClaimSerializer

def dashboard_view(request):
    return render(request, 'dashboard.html')

class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.all().order_by('-created_at')
    serializer_class = ExpenseClaimSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(employee=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        claim = self.get_object()
        claim.status = ExpenseClaim.Status.APPROVED
        claim.save()
        return Response({'status': 'Approved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        claim = self.get_object()
        claim.status = ExpenseClaim.Status.REJECTED
        claim.save()
        return Response({'status': 'Rejected'}, status=status.HTTP_200_OK)