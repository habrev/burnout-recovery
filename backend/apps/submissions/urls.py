from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit, name='submit'),
    path('results/', views.results, name='results'),
    path('results/<uuid:pk>/', views.result_detail, name='result-detail'),
    path('results/<uuid:pk>/feedback/', views.submit_feedback, name='submit-feedback'),
    path('results/<uuid:pk>/checked-actions/', views.update_checked_actions, name='update-checked-actions'),
]
