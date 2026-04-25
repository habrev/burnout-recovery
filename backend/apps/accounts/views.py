import random
import string
import uuid
from datetime import timedelta

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, OTPToken
from .serializers import UserSerializer


def _generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def _issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    """
    Registration step 1: send OTP to verify email ownership.
    No User row is created here — only an OTPToken tied to the email.
    """
    email = request.data.get('email', '').strip().lower()
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Invalidate any previous pending OTPs for this email
    OTPToken.objects.filter(email=email, is_used=False).update(is_used=True)

    code = _generate_otp()
    expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    OTPToken.objects.create(email=email, token=code, expires_at=expires_at)

    try:
        send_mail(
            subject='Verify your RESET account',
            message=(
                f'Your verification code is: {code}\n\n'
                f'This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n\n'
                f'If you did not request this, ignore this email.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        print(f'Email error: {e}')
        return Response(
            {'error': 'Failed to send email. Check the address and try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({'message': 'Verification code sent to your email.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Registration step 2: verify OTP, return a registration_token for the password step.
    Still no User row created.
    """
    email = request.data.get('email', '').strip().lower()
    code = request.data.get('code', '').strip()

    if not email or not code:
        return Response({'error': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

    otp = OTPToken.objects.filter(email=email, is_used=False).order_by('-created_at').first()

    if not otp or not otp.is_valid():
        return Response(
            {'error': 'Code expired or invalid. Request a new one.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    otp.attempts += 1

    if otp.token != code:
        otp.save()
        remaining = max(0, 3 - otp.attempts)
        return Response(
            {'error': f'Wrong code. {remaining} attempt(s) left.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    reg_token = uuid.uuid4()
    otp.registration_token = reg_token
    otp.expires_at = timezone.now() + timedelta(minutes=15)
    otp.is_used = True
    otp.save()

    return Response({
        'message': 'Email verified.',
        'registration_token': str(reg_token),
        'email': email,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Registration step 3: create the User row and set the password.
    This is the ONLY place a User is created during registration.
    """
    email = request.data.get('email', '').strip().lower()
    reg_token = request.data.get('registration_token', '').strip()
    password = request.data.get('password', '')

    if not email or not reg_token or not password:
        return Response(
            {'error': 'Email, registration token, and password are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        otp = OTPToken.objects.get(
            email=email,
            registration_token=reg_token,
            is_used=True,
        )
    except OTPToken.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired registration session. Please start over.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if otp.expires_at < timezone.now():
        return Response(
            {'error': 'Registration session expired. Please start over.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Create User only now — after password is confirmed
    try:
        user = User.objects.get(email=email)
        if user.has_usable_password():
            return Response(
                {'error': 'An account with this email is already registered. Please sign in.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except User.DoesNotExist:
        user = User(email=email)

    user.set_password(password)

    admin_emails = getattr(settings, 'ADMIN_EMAILS', [])
    if email in admin_emails:
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

    user.save()

    otp.registration_token = None
    otp.save()

    return Response(_issue_tokens(user), status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """Login with email + password."""
    email = request.data.get('email', '').strip().lower()
    password = request.data.get('password', '')

    if not email or not password:
        return Response(
            {'error': 'Email and password are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=email, password=password)

    if not user:
        if not User.objects.filter(email=email).exists():
            return Response(
                {'error': 'No account found with this email. Please create one.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {'error': 'Incorrect password.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if not user.is_active:
        return Response({'error': 'Account is disabled.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response(_issue_tokens(user))


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    from rest_framework_simplejwt.serializers import TokenRefreshSerializer
    serializer = TokenRefreshSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
    except Exception:
        return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email', '').strip().lower()
    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    if not User.objects.filter(email=email).exists():
        return Response({'error': 'No account found with this email.'}, status=status.HTTP_400_BAD_REQUEST)

    OTPToken.objects.filter(email=email, is_used=False).update(is_used=True)

    code = _generate_otp()
    expires_at = timezone.now() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)
    OTPToken.objects.create(email=email, token=code, expires_at=expires_at)

    try:
        send_mail(
            subject='Reset your RESET password',
            message=(
                f'Your password reset code is: {code}\n\n'
                f'This code expires in {settings.OTP_EXPIRY_MINUTES} minutes.\n\n'
                f'If you did not request this, ignore this email.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        print(f'Email error: {e}')
        return Response(
            {'error': 'Failed to send email. Check the address and try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({'message': 'Password reset code sent to your email.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_reset_otp(request):
    email = request.data.get('email', '').strip().lower()
    code = request.data.get('code', '').strip()

    if not email or not code:
        return Response({'error': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

    otp = OTPToken.objects.filter(email=email, is_used=False).order_by('-created_at').first()

    if not otp or not otp.is_valid():
        return Response(
            {'error': 'Code expired or invalid. Request a new one.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    otp.attempts += 1

    if otp.token != code:
        otp.save()
        remaining = max(0, 3 - otp.attempts)
        return Response(
            {'error': f'Wrong code. {remaining} attempt(s) left.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    reset_token = uuid.uuid4()
    otp.registration_token = reset_token
    otp.expires_at = timezone.now() + timedelta(minutes=15)
    otp.is_used = True
    otp.save()

    return Response({
        'message': 'Code verified.',
        'reset_token': str(reset_token),
        'email': email,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email', '').strip().lower()
    reset_token = request.data.get('reset_token', '').strip()
    password = request.data.get('password', '')

    if not email or not reset_token or not password:
        return Response(
            {'error': 'Email, reset token, and password are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if len(password) < 8:
        return Response(
            {'error': 'Password must be at least 8 characters'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        otp = OTPToken.objects.get(
            email=email,
            registration_token=reset_token,
            is_used=True,
        )
    except OTPToken.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired reset session. Please start over.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if otp.expires_at < timezone.now():
        return Response(
            {'error': 'Reset session expired. Please start over.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'No account found with this email.'}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(password)
    user.save()

    otp.registration_token = None
    otp.save()

    return Response({'message': 'Password reset successfully. Please sign in.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)
