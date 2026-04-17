from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Submission, Feedback
from .serializers import SubmissionSerializer
from ai_module import analyze_burnout
from engine import get_recovery_protocol


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit(request):
    input_text = request.data.get('input_text', '').strip()
    if not input_text:
        return Response({'error': 'Input text is required'}, status=status.HTTP_400_BAD_REQUEST)

    ai_data = analyze_burnout(input_text)
    if not ai_data:
        return Response(
            {'error': 'AI analysis failed. Please try again.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    protocol = get_recovery_protocol(ai_data['stress_level_int'])

    combined_output = {**ai_data, **protocol}

    submission = Submission.objects.create(
        user=request.user,
        input_text=input_text,
        ai_output=combined_output,
    )

    return Response({
        'id': str(submission.id),
        'result': combined_output,
        'created_at': submission.created_at.isoformat(),
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def results(request):
    submissions = Submission.objects.filter(user=request.user)[:20]
    serializer = SubmissionSerializer(submissions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def result_detail(request, pk):
    try:
        submission = Submission.objects.get(id=pk, user=request.user)
    except Submission.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    return Response(SubmissionSerializer(submission).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request, pk):
    try:
        submission = Submission.objects.get(id=pk, user=request.user)
    except Submission.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    rating = request.data.get('rating')
    comment = request.data.get('comment', '').strip()

    if rating not in ['helpful', 'not_helpful']:
        return Response({'error': 'Rating must be "helpful" or "not_helpful"'}, status=status.HTTP_400_BAD_REQUEST)

    Feedback.objects.update_or_create(
        submission=submission,
        defaults={'rating': rating, 'comment': comment},
    )

    return Response({'message': 'Feedback saved'}, status=status.HTTP_200_OK)
