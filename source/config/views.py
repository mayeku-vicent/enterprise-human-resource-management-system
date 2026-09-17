from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request, format=None):
    return Response({
        'token-obtain': reverse('token_obtain_pair', request=request, format=format),
        'token-refresh': reverse('token_refresh', request=request, format=format),
        'accounts': reverse('user-list', request=request, format=format),
        'departments': reverse('department-list', request=request, format=format),
        'positions': reverse('position-list', request=request, format=format),
        'leave-requests': reverse('leaverequest-list', request=request, format=format),
        'expense-claims': reverse('expenseclaim-list', request=request, format=format),
    })