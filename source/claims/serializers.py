from rest_framework import serializers
from .models import ExpenseClaim

class ExpenseClaimSerializer(serializers.ModelSerializer):
    employee_username = serializers.ReadOnlyField(source='employee.username')

    class Meta:
        model = ExpenseClaim
        fields = [
            'id', 
            'employee', 
            'employee_username', 
            'claim_type', 
            'amount', 
            'description', 
            'status', 
            'created_at'
        ]
        read_only_fields = ['id', 'employee', 'status', 'created_at']