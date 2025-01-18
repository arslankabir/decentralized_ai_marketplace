from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class CustomUser(AbstractUser):
    """
    Extended user model for the AI Task Marketplace
    """
    wallet_address = models.CharField(max_length=42, unique=True, null=True, blank=True)
    is_freelancer = models.BooleanField(default=False)
    skills = models.JSONField(default=list)
    reputation_score = models.FloatField(default=0.0)
    total_tasks_completed = models.IntegerField(default=0)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_groups',
        related_query_name='custom_user_group'
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_permissions',
        related_query_name='custom_user_permission'
    )

    def __str__(self):
        return self.username
