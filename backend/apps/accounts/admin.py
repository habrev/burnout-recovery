from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_admin', 'is_active', 'created_at')
    list_filter = ('is_admin', 'is_active')
    search_fields = ('email',)
    ordering = ('-created_at',)
    fieldsets = (
        (None, {'fields': ('email',)}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {'fields': ('email',)}),
    )
    filter_horizontal = ()


@admin.register(OTPToken)
class OTPTokenAdmin(admin.ModelAdmin):
    list_display = ('email', 'token', 'is_used', 'attempts', 'expires_at', 'created_at')
    list_filter = ('is_used',)
    search_fields = ('email',)
