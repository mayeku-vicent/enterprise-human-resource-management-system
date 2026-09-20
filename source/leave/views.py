from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by('-created_at')
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        if self.request.user and self.request.user.is_authenticated:
            serializer.save(employee=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.Status.APPROVED
        leave.save()
        return Response({'status': 'Approved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.Status.REJECTED
        leave.save()
        return Response({'status': 'Rejected'}, status=status.HTTP_200_OK)

def leave_dashboard_view(request):
    return render(request, 'leave_dashboard.html')