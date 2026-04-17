from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.admin_users, name='admin-users'),
    path('users/<uuid:pk>/', views.admin_user_detail, name='admin-user-detail'),
    path('results/', views.admin_results, name='admin-results'),
]
