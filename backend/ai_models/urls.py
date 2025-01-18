from django.urls import path
from .views import FreelancerRecommendationView, WorkValidationView

urlpatterns = [
    path('recommend-freelancers/', FreelancerRecommendationView.as_view(), name='ai-recommend-freelancers'),
    path('validate-submission/', WorkValidationView.as_view(), name='ai-validate-submission'),
]
