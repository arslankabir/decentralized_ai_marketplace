from django.contrib import admin
from .models import Task, TaskSubmission

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'assigned_freelancer', 'budget', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'description')

@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'freelancer', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('submission_text',)
