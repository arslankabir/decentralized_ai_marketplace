from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tasks.models import Task
from ai_models.models import FreelancerProfile
from ai_models.recommendation import FreelancerRecommendationEngine
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Test the AI recommendation model with various scenarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose', 
            action='store_true', 
            help='Print detailed recommendation information'
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        # Ensure we have tasks and freelancers
        tasks = list(Task.objects.all())
        freelancers = list(FreelancerProfile.objects.all())
        
        if not tasks or not freelancers:
            self.stdout.write(self.style.ERROR(
                'No tasks or freelancers found. Run generate_recommendation_data first.'
            ))
            return

        # Get or create a task creator
        try:
            task_creator = User.objects.first() or User.objects.create_user(
                username='test_creator', 
                email='creator@example.com', 
                password='testpassword123'
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating task creator: {e}'))
            return

        # Test different recommendation scenarios
        scenarios = [
            ('web development', ['web', 'JavaScript', 'Python', 'Django', 'Flask']),
            ('machine learning', ['machine', 'Python', 'TensorFlow', 'ML', 'Data Science']),
            ('blockchain', ['blockchain', 'Solidity', 'Web3', 'Smart Contracts', 'Ethereum']),
            ('mobile app development', ['mobile', 'Swift', 'Kotlin', 'React Native', 'Flutter'])
        ]

        for scenario, scenario_skills in scenarios:
            self.stdout.write(f"\n--- Testing Recommendations for {scenario.upper()} ---")
            
            # Create a test task
            test_task = Task.objects.create(
                creator=task_creator,
                title=f'Test Task: {scenario}',
                description=f'A sample task in {scenario}',
                skills_required=scenario_skills[:2],  # Use first two skills
                budget=1000
            )

            try:
                # Get recommendations
                recommended_freelancers = FreelancerRecommendationEngine.recommend_freelancers(
                    test_task, top_n=3
                )

                if verbose:
                    self.stdout.write("\nRecommended Freelancers:")
                    for idx, freelancer in enumerate(recommended_freelancers, 1):
                        self.stdout.write(f"{idx}. {freelancer.user.username}")
                        self.stdout.write(f"   Skills: {freelancer.skill_embedding}")
                        self.stdout.write(f"   Performance Score: {freelancer.performance_score}")
                        
                        # Check skill match
                        matched_skills = set(scenario_skills) & set(freelancer.skill_embedding)
                        self.stdout.write(f"   Matched Skills: {matched_skills}\n")

                # Basic validation
                if len(recommended_freelancers) > 0:
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully found {len(recommended_freelancers)} recommendations'
                    ))
                else:
                    self.stdout.write(self.style.WARNING(
                        'No recommendations found for this scenario'
                    ))

            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error in recommendation for {scenario}: {e}'
                ))
                logger.error(f'Recommendation error: {e}')

            # Clean up test task
            test_task.delete()

        # Overall model performance analysis
        self.analyze_model_performance()

    def analyze_model_performance(self):
        """
        Perform a basic performance analysis of the recommendation model
        """
        from ai_models.models import AIModelTrainingLog
        
        # Fetch the latest training log
        latest_log = AIModelTrainingLog.objects.first()
        
        if latest_log:
            self.stdout.write("\n--- Model Performance Analysis ---")
            self.stdout.write(f"Training Data Size: {latest_log.training_data_size}")
            self.stdout.write(f"Training Accuracy: {latest_log.training_accuracy}")
            self.stdout.write(f"Captured at: {latest_log.captured_at}")
        else:
            self.stdout.write(self.style.WARNING(
                'No training logs found. Train the model first.'
            ))
