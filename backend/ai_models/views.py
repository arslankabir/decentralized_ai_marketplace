import os
import joblib
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from django.conf import settings

from .models import AIModelTrainingLog, FreelancerProfile
from users.models import CustomUser
from tasks.models import Task, TaskSubmission

class FreelancerRecommendationView(APIView):
    """
    AI-powered freelancer recommendation endpoint
    """
    permission_classes = [permissions.IsAuthenticated]

    def load_recommendation_model(self):
        """
        Load pre-trained recommendation model
        """
        model_path = os.path.join(
            settings.BASE_DIR, 
            'ai_models', 
            'training_scripts', 
            'freelancer_recommender_model', 
            'model.joblib'
        )
        scaler_path = os.path.join(
            settings.BASE_DIR, 
            'ai_models', 
            'training_scripts', 
            'freelancer_recommender_model', 
            'scaler.joblib'
        )
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        return model, scaler

    def post(self, request):
        """
        Recommend freelancers for a given task
        """
        task_id = request.data.get('task_id')
        
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Load model
        model, scaler = self.load_recommendation_model()

        # Get all freelancers
        freelancers = CustomUser.objects.filter(is_freelancer=True)
        
        recommendations = []
        for freelancer in freelancers:
            # Prepare feature vector
            skill_vector = self._skills_to_vector(freelancer.skills)
            
            features = [
                len(Task.objects.filter(submissions__freelancer=freelancer, status='COMPLETED')),
                freelancer.reputation_score,
                *skill_vector
            ]

            # Scale features
            features_scaled = scaler.transform([features])
            
            # Predict recommendation score
            recommendation_score = model.predict(features_scaled)[0]
            
            recommendations.append({
                'freelancer_id': freelancer.id,
                'username': freelancer.username,
                'recommendation_score': float(recommendation_score)
            })

        # Sort recommendations by score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return Response(recommendations[:5])  # Top 5 recommendations

    def _skills_to_vector(self, skills, max_skills=10):
        """
        Convert skills to a numerical vector
        """
        skill_dict = {
            'Python': 1, 'AI': 2, 'Machine Learning': 3,
            'Web Development': 4, 'Data Science': 5,
        }
        
        vector = [0] * max_skills
        for i, skill in enumerate(skills[:max_skills]):
            vector[i] = skill_dict.get(skill, 0)
        
        return vector

class WorkValidationView(APIView):
    """
    AI-powered work validation endpoint
    """
    permission_classes = [permissions.IsAuthenticated]

    def load_validation_model(self):
        """
        Load pre-trained work validation model
        """
        model_path = os.path.join(
            settings.BASE_DIR, 
            'ai_models', 
            'training_scripts', 
            'work_validator_model', 
            'model.joblib'
        )
        scaler_path = os.path.join(
            settings.BASE_DIR, 
            'ai_models', 
            'training_scripts', 
            'work_validator_model', 
            'scaler.joblib'
        )
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        return model, scaler

    def post(self, request):
        """
        Validate a task submission
        """
        submission_id = request.data.get('submission_id')
        
        try:
            submission = TaskSubmission.objects.get(id=submission_id)
        except TaskSubmission.DoesNotExist:
            return Response(
                {'error': 'Submission not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Load model
        model, scaler = self.load_validation_model()

        # Prepare feature vector
        features = [
            submission.task.budget,
            len(submission.task.description),
            submission.freelancer.reputation_score,
            submission.task.skills_required.count(),
            submission.submitted_at.timestamp(),
        ]

        # Scale features
        features_scaled = scaler.transform([features])
        
        # Predict validation
        validation_prob = model.predict_proba(features_scaled)[0][1]
        is_valid = validation_prob > 0.5

        return Response({
            'submission_id': submission.id,
            'is_valid': bool(is_valid),
            'validation_probability': float(validation_prob)
        })
