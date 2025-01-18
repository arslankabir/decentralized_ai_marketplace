from django.contrib import admin
from .models import AIModelTrainingLog, FreelancerProfile, AIModel, AIModelVersion

# Register your models here.

@admin.register(AIModelTrainingLog)
class AIModelTrainingLogAdmin(admin.ModelAdmin):
    list_display = ('model_type', 'training_accuracy', 'captured_at', 'is_used_for_training')
    list_filter = ('model_type', 'captured_at', 'is_used_for_training')
    search_fields = ('model_version',)

@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'performance_score')
    search_fields = ('user__username',)

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(AIModelVersion)
class AIModelVersionAdmin(admin.ModelAdmin):
    list_display = ('model', 'version', 'created_at')
    list_filter = ('model', 'created_at')
    search_fields = ('version',)
