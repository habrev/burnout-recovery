from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/', include('apps.submissions.urls')),
    path('api/admin4reset/', include('apps.admin_panel.urls')),
]
