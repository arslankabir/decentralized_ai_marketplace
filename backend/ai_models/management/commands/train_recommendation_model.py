from django.core.management.base import BaseCommand
from django.db import transaction
from tasks.models import Task
from ai_models.models import FreelancerProfile, AIModelTrainingLog
from ai_models.recommendation import FreelancerRecommendationEngine
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Train the AI recommendation model for freelancers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--min-tasks', 
            type=int, 
            default=50, 
            help='Minimum number of tasks required to train the model'
        )
        parser.add_argument(
            '--min-freelancers', 
            type=int, 
            default=20, 
            help='Minimum number of freelancers required to train the model'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Configure logging
        logging.basicConfig(level=logging.INFO)

        # Fetch all tasks and freelancer profiles
        tasks = Task.objects.all()
        freelancers = FreelancerProfile.objects.all()

        # Log current data stats
        logger.info(f"Current data stats: Tasks={len(tasks)}, Freelancers={len(freelancers)}")

        # Check if there are enough data points
        if len(tasks) < options['min_tasks'] or len(freelancers) < options['min_freelancers']:
            error_msg = (
                f'Not enough data to train the model. '
                f'Current stats: Tasks={len(tasks)}, Freelancers={len(freelancers)}. '
                f'Minimum required: Tasks={options["min_tasks"]}, '
                f'Freelancers={options["min_freelancers"]}'
            )
            logger.error(error_msg)
            self.stdout.write(self.style.WARNING(error_msg))
            return

        try:
            # Train the recommendation model
            logger.info('Starting model training...')
            self.stdout.write('Starting model training...')

            model, scaler = FreelancerRecommendationEngine.train_recommendation_model(
                tasks, freelancers
            )

            # Log successful training
            training_log = AIModelTrainingLog.objects.create(
                model_type='FREELANCER_REC',
                training_data={
                    'tasks_count': len(tasks),
                    'freelancers_count': len(freelancers)
                },
                training_accuracy=model.score(scaler.transform(model.X), model.y),
                training_data_size=len(model.X),
                is_used_for_training=True
            )

            logger.info(f'Model training completed. Training log ID: {training_log.id}')
            self.stdout.write(self.style.SUCCESS(
                f'Recommendation model trained successfully! Training log ID: {training_log.id}'
            ))

        except Exception as e:
            logger.error(f'Error training recommendation model: {e}')
            self.stdout.write(self.style.ERROR(
                f'Failed to train recommendation model: {e}'
            ))
