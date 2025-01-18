from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from tasks.models import Task
from ai_models.models import FreelancerProfile
from users.models import CustomUser  # Import the custom user model
import random
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Generate synthetic data for AI recommendation system'

    def add_arguments(self, parser):
        parser.add_argument('--tasks', type=int, default=200, help='Number of tasks to generate')
        parser.add_argument('--freelancers', type=int, default=100, help='Number of freelancers to generate')

    def _create_unique_user(self, username_base, is_freelancer=False):
        """
        Create a unique user with a unique username
        """
        # Try to create a unique username
        username = username_base
        counter = 0
        while CustomUser.objects.filter(username=username).exists():
            counter += 1
            username = f"{username_base}_{counter}"

        # Create user with minimal required fields
        user = CustomUser.objects.create(
            username=username, 
            email=f"{username}@example.com",
            is_freelancer=is_freelancer
        )
        user.set_password('testpassword123')
        user.save()
        return user

    def handle(self, *args, **options):
        # Configure logging
        logging.basicConfig(level=logging.INFO)

        # Safely clear existing data
        self.clear_existing_data()

        # Define skill categories
        skill_categories = {
            'web_dev': ['Python', 'JavaScript', 'React', 'Django', 'Flask'],
            'mobile_dev': ['Swift', 'Kotlin', 'React Native', 'Flutter'],
            'data_science': ['Machine Learning', 'Python', 'R', 'TensorFlow', 'Pandas'],
            'design': ['UI/UX', 'Figma', 'Photoshop', 'Illustrator'],
            'blockchain': ['Solidity', 'Web3', 'Smart Contracts', 'Ethereum']
        }

        # Wrap the entire data generation in a transaction
        with transaction.atomic():
            # Create a default task creator
            task_creator = self._create_unique_user('task_creator', is_freelancer=False)

            # Generate freelancers
            freelancers = []
            all_skills = [skill for skills in skill_categories.values() for skill in skills]

            for i in range(options['freelancers']):
                # Create user with unique username
                user = self._create_unique_user(f'freelancer_{i}', is_freelancer=True)

                # Randomly select skills
                num_skills = random.randint(2, 5)
                skills = random.sample(all_skills, num_skills)

                # Create freelancer profile
                profile = FreelancerProfile.objects.create(
                    user=user,
                    skill_embedding=skills,
                    performance_score=random.uniform(0.5, 1.0)
                )
                freelancers.append(profile)

            # Generate tasks
            tasks = []
            for i in range(options['tasks']):
                # Randomly select task category
                category = random.choice(list(skill_categories.keys()))
                skills = skill_categories[category]

                # Create task
                task = Task.objects.create(
                    creator=task_creator,
                    title=f'Synthetic Task {i} - {category.replace("_", " ").title()}',
                    description=f'A sample task in the {category} domain',
                    budget=random.uniform(100, 5000),
                    skills_required=random.sample(skills, random.randint(1, len(skills)))
                )
                tasks.append(task)

            # Log generation results
            logger.info(f'Generated {len(tasks)} tasks and {len(freelancers)} freelancers')
            self.stdout.write(self.style.SUCCESS(
                f'Generated {len(tasks)} tasks and {len(freelancers)} freelancers'
            ))

    def clear_existing_data(self):
        """
        Safely clear existing synthetic data
        """
        try:
            # Delete tasks first to avoid foreign key constraints
            Task.objects.filter(
                Q(title__startswith='Synthetic Task') | 
                Q(creator__username='task_creator')
            ).delete()

            # Delete freelancer profiles
            FreelancerProfile.objects.all().delete()

            # Delete specific users
            CustomUser.objects.filter(
                Q(username__startswith='freelancer_') | 
                Q(username='task_creator')
            ).delete()
        except Exception as e:
            logger.error(f"Error clearing existing data: {e}")
