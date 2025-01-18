from django.db import models
from django.conf import settings
from django.utils import timezone

class Task(models.Model):
    """
    Represents a task in the decentralized marketplace
    """
    TASK_STATUS_CHOICES = [
        ('CREATED', 'Created'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED', 'Submitted'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_freelancer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='assigned_tasks', 
        null=True, 
        blank=True
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    skills_required = models.JSONField(default=list)
    
    status = models.CharField(
        max_length=20, 
        choices=TASK_STATUS_CHOICES, 
        default='CREATED'
    )
    
    blockchain_task_id = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def recommend_freelancers(self, top_n=5):
        """
        Recommend top freelancers for this task
        """
        from ai_models.recommendation import FreelancerRecommendationEngine
        return FreelancerRecommendationEngine.recommend_freelancers(self, top_n)

    def __str__(self):
        return self.title

class TaskSubmission(models.Model):
    """
    Represents a task submission by a freelancer
    """
    SUBMISSION_STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    freelancer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    submission_file = models.FileField(upload_to='task_submissions/', null=True, blank=True)
    submission_text = models.TextField()
    
    status = models.CharField(
        max_length=20, 
        choices=SUBMISSION_STATUS_CHOICES, 
        default='PENDING'
    )
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Submission for {self.task.title} by {self.freelancer.username}"
