from rest_framework import serializers
from .models import ExpenseClaim

class ExpenseClaimSerializer(serializers.ModelSerializer):
    employee_username = serializers.ReadOnlyField(source='employee.username')
    approved_by_username = serializers.ReadOnlyField(source='approved_by.username')

    class Meta:
        model = ExpenseClaim
        fields = [
            'id', 'employee', 'employee_username', 'claim_type', 
            'amount', 'description', 'status', 
            'approved_by', 'approved_by_username', 'created_at'
        ]
        read_only_fields = ['id', 'employee', 'status', 'approved_by', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['employee'] = request.user
        return super().create(validated_data)