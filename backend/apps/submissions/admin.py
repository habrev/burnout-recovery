from django.contrib import admin
from .models import Submission, Feedback


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'stress_level', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'input_text')
    ordering = ('-created_at',)

    def stress_level(self, obj):
        return obj.ai_output.get('stress_level_int', '—')
    stress_level.short_description = 'Stress'


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('submission', 'rating', 'created_at')
    list_filter = ('rating',)
