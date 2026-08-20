from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Attainment
from .serializers import AttainmentSerializer
from .services import calculate_for_course


class AttainmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only for normal CRUD (GET list/retrieve only) — attainments are never
    edited by hand, only ever written via the /calculate/ action below.
    """
    queryset = Attainment.objects.all()
    serializer_class = AttainmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        course_id = self.request.query_params.get('course')
        return qs.filter(course_id=course_id) if course_id else qs

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """POST { "course": <id> } -> recalculates and returns attainment for every CO in that course."""
        course_id = request.data.get('course')
        if not course_id:
            return Response({'error': 'course is required'}, status=400)
        results = calculate_for_course(course_id)
        return Response(AttainmentSerializer(results, many=True).data)