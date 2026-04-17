from rest_framework import serializers
from apps.accounts.models import User
from apps.submissions.models import Submission, Feedback


class AdminFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment', 'created_at']


class AdminSubmissionSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    feedback = AdminFeedbackSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'user_email', 'input_text', 'ai_output', 'created_at', 'feedback']


class AdminUserSerializer(serializers.ModelSerializer):
    submission_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'is_admin', 'created_at', 'submission_count']

    def get_submission_count(self, obj):
        return obj.submissions.count()
