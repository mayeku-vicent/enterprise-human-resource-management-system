from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ExpenseClaim
from .serializers import ExpenseClaimSerializer

class ExpenseClaimViewSet(viewsets.ModelViewSet):
  
    queryset = ExpenseClaim.objects.all().order_by('-created_at')
    serializer_class = ExpenseClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        claim = self.get_object()
        claim.status = ExpenseClaim.Status.APPROVED
        claim.approved_by = request.user
        claim.save()
        return Response({'status': 'Claim request approved successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        claim = self.get_object()
        claim.status = ExpenseClaim.Status.REJECTED
        claim.approved_by = request.user
        claim.save()
        return Response({'status': 'Claim request rejected.'}, status=status.HTTP_200_OK)