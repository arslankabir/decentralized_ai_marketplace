from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from .models import Task, TaskSubmission
from ai_models.models import FreelancerProfile

@csrf_exempt
@require_http_methods(["POST"])
def create_task(request):
    """
    Create a new task
    """
    try:
        data = json.loads(request.body)
        task = Task.objects.create(
            creator=request.user,
            title=data.get('title'),
            description=data.get('description'),
            budget=data.get('budget'),
            skills_required=data.get('skills_required', [])
        )
        return JsonResponse({
            'status': 'success', 
            'task_id': task.id
        }, status=201)
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def list_tasks(request):
    """
    List tasks with optional filtering
    """
    tasks = Task.objects.all()
    return JsonResponse({
        'tasks': list(tasks.values())
    })

@require_http_methods(["GET"])
def task_detail(request, task_id):
    """
    Get task details
    """
    try:
        task = Task.objects.get(id=task_id)
        return JsonResponse(task.__dict__)
    except Task.DoesNotExist:
        return JsonResponse({
            'status': 'error', 
            'message': 'Task not found'
        }, status=404)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def submit_task(request, task_id):
    """
    Submit work for a task
    """
    try:
        task = Task.objects.get(id=task_id)
        data = json.loads(request.body)
        
        submission = TaskSubmission.objects.create(
            task=task,
            freelancer=request.user,
            submission_text=data.get('submission_text'),
            submission_file=data.get('submission_file')
        )
        
        return JsonResponse({
            'status': 'success', 
            'submission_id': submission.id
        }, status=201)
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def validate_task(request, task_id):
    """
    Validate task submission
    """
    try:
        task = Task.objects.get(id=task_id)
        data = json.loads(request.body)
        
        submission = TaskSubmission.objects.get(
            id=data.get('submission_id'), 
            task=task
        )
        
        # Update submission status
        submission.status = data.get('status', 'APPROVED')
        submission.save()
        
        return JsonResponse({
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)

@require_http_methods(["GET"])
def recommend_freelancers(request, task_id):
    """
    Get recommended freelancers for a task
    """
    try:
        task = Task.objects.get(id=task_id)
        
        # Get top 5 recommended freelancers
        recommendations = task.recommend_freelancers(top_n=5)
        
        # Convert recommendations to JSON-serializable format
        recommended_freelancers = []
        for rec in recommendations:
            freelancer = rec['freelancer']
            recommended_freelancers.append({
                'user_id': freelancer.user.id,
                'username': freelancer.user.username,
                'performance_score': freelancer.performance_score,
                'skills': freelancer.skill_embedding,
                'match_score': rec['match_score']
            })
        
        return JsonResponse({
            'task_id': task_id,
            'recommended_freelancers': recommended_freelancers
        })
    except Task.DoesNotExist:
        return JsonResponse({
            'status': 'error', 
            'message': 'Task not found'
        }, status=404)
