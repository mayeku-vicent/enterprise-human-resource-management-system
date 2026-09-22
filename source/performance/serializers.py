from rest_framework import serializers
from .models import PerformanceGoal, Appraisal

class PerformanceGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceGoal
        fields = '__all__'

class AppraisalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appraisal
        fields = '__all__'