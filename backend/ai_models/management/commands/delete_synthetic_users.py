from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from tasks.models import Task, TaskSubmission
from ai_models.models import AIModelTrainingLog, FreelancerProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Delete synthetic users created for testing'

    @transaction.atomic
    def handle(self, *args, **options):
        # Delete synthetic task submissions
        TaskSubmission.objects.filter(
            task__title__startswith='Synthetic Task'
        ).delete()

        # Delete synthetic tasks
        Task.objects.filter(
            title__startswith='Synthetic Task'
        ).delete()

        # Delete synthetic freelancer profiles
        FreelancerProfile.objects.filter(
            user__username__startswith='freelancer_'
        ).delete()

        # Delete synthetic freelancers
        deleted_count, _ = User.objects.filter(
            username__startswith='freelancer_'
        ).delete()

        # Delete task creator
        User.objects.filter(username='task_creator').delete()

        # Delete AI training logs
        AIModelTrainingLog.objects.filter(
            model_type__in=['FREELANCER_REC', 'WORK_VALIDATION']
        ).delete()

        self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} synthetic users and related data'))
