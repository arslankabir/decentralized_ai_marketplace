import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
import joblib
import os
import json
import logging
from django.contrib.auth import get_user_model
from tasks.models import Task
from ai_models.models import FreelancerProfile, AIModelTrainingLog

logger = logging.getLogger(__name__)
User = get_user_model()

class FreelancerRecommendationEngine:
    """
    AI-powered recommendation engine for matching freelancers to tasks
    """
    
    @staticmethod
    def _extract_features(tasks, freelancers):
        """
        Extract features for tasks and freelancers
        """
        # Extract skills from tasks and freelancers
        task_skills = [' '.join(task.skills_required) for task in tasks]
        freelancer_skills = [' '.join(profile.skill_embedding) for profile in freelancers]

        # Use TF-IDF to vectorize skills
        vectorizer = TfidfVectorizer()
        task_skill_vectors = vectorizer.fit_transform(task_skills)
        freelancer_skill_vectors = vectorizer.transform(freelancer_skills)

        return task_skill_vectors, freelancer_skill_vectors, vectorizer

    @staticmethod
    def train_recommendation_model(tasks, freelancers):
        """
        Train a recommendation model using task and freelancer skills
        """
        # Check if there are enough data points
        if len(tasks) < 10 or len(freelancers) < 5:
            raise ValueError(
                f"Insufficient data for training. "
                f"Tasks: {len(tasks)}, Freelancers: {len(freelancers)}"
            )

        # Extract features
        task_vectors, freelancer_vectors, vectorizer = FreelancerRecommendationEngine._extract_features(
            tasks, freelancers
        )

        # Compute similarity matrix
        similarity_matrix = cosine_similarity(task_vectors, freelancer_vectors)

        # Prepare training data with meaningful labels
        X = []
        y = []

        for i, task in enumerate(tasks):
            # Find top 3 most similar freelancers for each task
            task_similarities = similarity_matrix[i]
            top_freelancer_indices = task_similarities.argsort()[-3:][::-1]

            for j, freelancer_idx in enumerate(top_freelancer_indices):
                # Create a training sample
                X.append([
                    task_similarities[freelancer_idx],  # Similarity score
                    freelancers[int(freelancer_idx)].performance_score,  # Freelancer performance
                    len(set(task.skills_required) & set(freelancers[int(freelancer_idx)].skill_embedding))  # Skill match
                ])
                
                # Label: 1 for top match, 0 for less relevant
                y.append(1 if j == 0 else 0)

        # Convert to numpy arrays
        X = np.array(X)
        y = np.array(y)

        # Train a simple logistic regression model
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = LogisticRegression(random_state=42)
        model.fit(X_scaled, y)

        # Attach X and y to the model for later use
        model.X = X
        model.y = y

        # Save model and vectorizer
        base_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(base_dir, 'trained_models')
        os.makedirs(models_dir, exist_ok=True)

        joblib.dump(model, os.path.join(models_dir, 'recommendation_model.pkl'))
        joblib.dump(vectorizer, os.path.join(models_dir, 'skill_vectorizer.pkl'))
        joblib.dump(scaler, os.path.join(models_dir, 'feature_scaler.pkl'))

        # Log training details
        AIModelTrainingLog.objects.create(
            model_type='FREELANCER_REC',
            training_data=json.dumps({
                'tasks_count': len(tasks),
                'freelancers_count': len(freelancers)
            }),
            training_accuracy=model.score(X_scaled, y),
            training_data_size=len(X),
            is_used_for_training=True
        )

        return model, scaler

    @staticmethod
    def recommend_freelancers(task, top_n=5):
        """
        Recommend top freelancers for a given task
        """
        # Load pre-trained model and vectorizer
        base_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(base_dir, 'trained_models')

        try:
            model = joblib.load(os.path.join(models_dir, 'recommendation_model.pkl'))
            vectorizer = joblib.load(os.path.join(models_dir, 'skill_vectorizer.pkl'))
            scaler = joblib.load(os.path.join(models_dir, 'feature_scaler.pkl'))

            # Vectorize task skills
            task_skills_str = ' '.join(task.skills_required)
            task_vector = vectorizer.transform([task_skills_str])

            # Get all freelancers
            freelancers = list(FreelancerProfile.objects.all())
            freelancer_skills = [' '.join(profile.skill_embedding) for profile in freelancers]
            freelancer_vectors = vectorizer.transform(freelancer_skills)

            # Compute similarities
            similarities = cosine_similarity(task_vector, freelancer_vectors)[0]

            # Prepare features for recommendation
            X_recommend = []
            for i, freelancer in enumerate(freelancers):
                X_recommend.append([
                    similarities[i],  # Similarity score
                    freelancer.performance_score,  # Freelancer performance
                    len(set(task.skills_required) & set(freelancer.skill_embedding))  # Skill match
                ])

            # Scale features
            X_recommend_scaled = scaler.transform(X_recommend)

            # Predict recommendation scores
            recommendation_scores = model.predict_proba(X_recommend_scaled)[:, 1]

            # Sort freelancers by recommendation score
            recommended_indices = recommendation_scores.argsort()[::-1][:top_n]
            recommended_freelancers = [freelancers[idx] for idx in recommended_indices]

            return recommended_freelancers

        except FileNotFoundError:
            # Train model if not found
            from django.core.management import call_command
            call_command('train_recommendation_model')
            return FreelancerRecommendationEngine.recommend_freelancers(task, top_n)
        except Exception as e:
            logger.error(f"Error recommending freelancers: {e}")
            return []
