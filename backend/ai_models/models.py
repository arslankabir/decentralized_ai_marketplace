from django.db import models
from django.conf import settings
from django.utils import timezone
import json

# Create your models here.

class AIModel(models.Model):
    """
    Represents different AI models used in the platform
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class AIModelVersion(models.Model):
    """
    Tracks different versions of AI models
    """
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=20)
    model_file = models.FileField(upload_to='ai_models/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.model.name} - {self.version}"

class AIModelTrainingLog(models.Model):
    """
    Log for tracking AI model training and data collection
    """
    MODEL_TYPES = [
        ('FREELANCER_REC', 'Freelancer Recommendation'),
        ('WORK_VALIDATION', 'Work Validation'),
    ]

    model_type = models.CharField(max_length=50, choices=MODEL_TYPES)
    model_version = models.CharField(max_length=20, null=True, blank=True)
    training_data = models.JSONField(null=True, blank=True)
    label = models.CharField(max_length=100, null=True, blank=True)
    training_accuracy = models.FloatField(null=True, blank=True)
    training_loss = models.FloatField(null=True, blank=True)
    training_data_size = models.IntegerField(null=True, blank=True)
    is_used_for_training = models.BooleanField(default=False)
    captured_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        """
        Ensure training data is JSON serializable
        """
        if self.training_data and not isinstance(self.training_data, str):
            try:
                self.training_data = json.dumps(self.training_data)
            except TypeError:
                self.training_data = str(self.training_data)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_model_type_display()} Training Log - {self.captured_at}"

    class Meta:
        verbose_name_plural = "AI Model Training Logs"
        ordering = ['-captured_at']

class FreelancerProfile(models.Model):
    """
    AI-enhanced freelancer profile for recommendation
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    skill_embedding = models.JSONField(default=list)
    task_history_embedding = models.JSONField(default=list)
    performance_score = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"AI Profile for {self.user.username}"
