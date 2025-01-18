import random
import json
import numpy as np
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from tasks.models import Task, TaskSubmission
from ai_models.models import AIModelTrainingLog, FreelancerProfile
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate synthetic training data and train AI models'

    @transaction.atomic
    def generate_synthetic_data(self):
        """
        Generate synthetic training data for AI models
        """
        # Skills and domains
        skills_list = [
            'Python', 'AI', 'Machine Learning', 'Web Development', 
            'Data Science', 'Blockchain', 'Frontend', 'Backend',
            'React', 'Django', 'TensorFlow', 'Cloud Computing'
        ]

        # Delete existing synthetic data
        AIModelTrainingLog.objects.filter(
            model_type__in=['FREELANCER_REC', 'WORK_VALIDATION']
        ).delete()
        
        TaskSubmission.objects.filter(
            task__title__startswith='Synthetic Task'
        ).delete()
        
        Task.objects.filter(
            title__startswith='Synthetic Task'
        ).delete()

        User.objects.filter(
            username__startswith='freelancer_'
        ).delete()

        # Create synthetic freelancers
        freelancers = []
        for i in range(50):  # Increased number of synthetic freelancers
            username = f'freelancer_{i}'
            user = User.objects.create(
                username=username,
                email=f'{username}@example.com', 
                is_active=True,
                is_freelancer=True,
                skills=random.sample(skills_list, random.randint(1, 4)),
                reputation_score=round(random.uniform(0.5, 5.0), 2)
            )
            user.set_password('testpass123')
            user.save()

            # Create AI-enhanced freelancer profile
            profile, _ = FreelancerProfile.objects.get_or_create(
                user=user,
                defaults={
                    'skill_embedding': user.skills,
                    'task_history_embedding': [],
                    'performance_score': user.reputation_score
                }
            )
            freelancers.append(user)

        # Synthetic task creator
        creator = User.objects.create(
            username='task_creator', 
            email='creator@example.com', 
            is_active=True
        )
        creator.set_password('testpass123')
        creator.save()

        # Generate synthetic tasks and submissions
        training_logs = []
        for _ in range(200):  # Increased number of synthetic tasks
            task_skills = random.sample(skills_list, random.randint(1, 3))
            
            task = Task.objects.create(
                creator=creator,
                title=f'Synthetic Task {random.randint(1, 5000)}',
                description=f'Synthetic task in {", ".join(task_skills)} domain',
                budget=Decimal(str(round(random.uniform(50, 5000), 2))),
                skills_required=task_skills,
                status='COMPLETED'
            )
            
            # Create task submissions
            for _ in range(random.randint(1, 5)):
                freelancer = random.choice(freelancers)
                submission = TaskSubmission.objects.create(
                    task=task,
                    freelancer=freelancer,
                    submission_text='Synthetic submission for training',
                    status=random.choice(['APPROVED', 'REJECTED'])
                )
                
                # Prepare feature vector for training
                feature_vector = [
                    float(task.budget),
                    len(task.description),
                    freelancer.reputation_score,
                    len(task_skills),
                    submission.submitted_at.timestamp()
                ]
                
                # Create training log
                training_log = AIModelTrainingLog.objects.create(
                    model_type='FREELANCER_REC',
                    training_data=feature_vector,
                    label=1 if submission.status == 'APPROVED' else 0,
                    training_accuracy=None,
                    captured_at=timezone.now()
                )
                training_logs.append(training_log)

        return training_logs

    def train_freelancer_recommendation_model(self, training_logs):
        """
        Train a RandomForest model for freelancer recommendation
        """
        # Prepare training data
        X = []
        y = []
        for log in training_logs:
            features = log.training_data
            X.append(features)
            y.append(log.label)

        if not X or not y:
            self.stdout.write(self.style.WARNING('No training data available'))
            return

        # Split and scale data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train RandomForest model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train_scaled, y_train)

        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred)

        # Save model and scaler
        joblib.dump(model, 'freelancer_recommendation_model.joblib')
        joblib.dump(scaler, 'freelancer_recommendation_scaler.joblib')

        # Update training logs
        AIModelTrainingLog.objects.filter(
            model_type='FREELANCER_REC', 
            training_accuracy__isnull=True
        ).update(
            training_accuracy=accuracy,
            is_used_for_training=True
        )

        self.stdout.write(self.style.SUCCESS(f'Model trained with accuracy: {accuracy}'))
        self.stdout.write(self.style.SUCCESS(f'Classification Report:\n{report}'))

    def handle(self, *args, **options):
        # Generate synthetic training data
        training_logs = self.generate_synthetic_data()
        
        # Train freelancer recommendation model
        self.train_freelancer_recommendation_model(training_logs)
        
        self.stdout.write(self.style.SUCCESS('Successfully generated training data and trained models'))
