from django.urls import path
from . import views

urlpatterns = [
    # Task-related endpoints
    path('create/', views.create_task, name='create_task'),
    path('list/', views.list_tasks, name='list_tasks'),
    path('<int:task_id>/', views.task_detail, name='task_detail'),
    path('<int:task_id>/submit/', views.submit_task, name='submit_task'),
    path('<int:task_id>/validate/', views.validate_task, name='validate_task'),
    path('<int:task_id>/recommend/', views.recommend_freelancers, name='recommend_freelancers'),
]
