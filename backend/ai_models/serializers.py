from rest_framework import serializers
from .models import AIModelTrainingLog, FreelancerProfile
from users.serializers import UserProfileSerializer

class AIModelTrainingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModelTrainingLog
        fields = '__all__'

class FreelancerProfileSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = FreelancerProfile
        fields = ['user', 'skill_embedding', 'task_history_embedding', 'performance_score']
