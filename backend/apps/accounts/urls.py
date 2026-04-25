from django.urls import path
from . import views

urlpatterns = [
    path('request-otp/', views.request_otp, name='request-otp'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('token/refresh/', views.token_refresh, name='token-refresh'),
    path('me/', views.me, name='me'),
    path('forgot-password/', views.forgot_password, name='forgot-password'),
    path('verify-reset-otp/', views.verify_reset_otp, name='verify-reset-otp'),
    path('reset-password/', views.reset_password, name='reset-password'),
]
