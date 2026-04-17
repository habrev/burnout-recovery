from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import User
from apps.submissions.models import Submission
from .serializers import AdminUserSerializer, AdminSubmissionSerializer


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin
        )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users(request):
    search = request.query_params.get('search', '').strip()
    users = User.objects.all().order_by('-created_at')
    if search:
        users = users.filter(email__icontains=search)
    return Response(AdminUserSerializer(users, many=True).data)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAdminUser])
def admin_user_detail(request, pk):
    try:
        user = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        is_admin = request.data.get('is_admin')
        if is_admin is not None:
            if user == request.user and not is_admin:
                return Response(
                    {'error': 'You cannot remove your own admin access'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.is_admin = bool(is_admin)
            user.is_staff = bool(is_admin)
            user.save()

    return Response(AdminUserSerializer(user).data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_results(request):
    search = request.query_params.get('search', '').strip()
    user_filter = request.query_params.get('user', '').strip()

    submissions = Submission.objects.select_related('user', 'feedback').order_by('-created_at')

    if search:
        submissions = submissions.filter(
            Q(input_text__icontains=search) | Q(user__email__icontains=search)
        )
    if user_filter:
        submissions = submissions.filter(user__email__icontains=user_filter)

    return Response(AdminSubmissionSerializer(submissions[:100], many=True).data)
