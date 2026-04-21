from rest_framework import serializers
from .models import Submission, Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment', 'created_at']
        read_only_fields = ['created_at']


class SubmissionSerializer(serializers.ModelSerializer):
    feedback = FeedbackSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'input_text', 'ai_output', 'checked_actions', 'created_at', 'feedback']
        read_only_fields = ['id', 'input_text', 'ai_output', 'created_at', 'feedback']
