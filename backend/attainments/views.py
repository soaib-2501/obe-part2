from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Attainment, ProgramAttainment
from .serializers import AttainmentSerializer, ProgramAttainmentSerializer
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

    @action(detail=False, methods=['get'])
    def program(self, request):
        course_id = request.query_params.get('course')
        qs = ProgramAttainment.objects.all()
        if course_id:
            qs = qs.filter(course_id=course_id)
        return Response(ProgramAttainmentSerializer(qs, many=True).data)

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """POST { "course": <id> } -> recalculates CO and PO/PSO attainment."""
        course_id = request.data.get('course')
        if not course_id:
            return Response({'error': 'course is required'}, status=400)
        co_results, po_results = calculate_for_course(course_id)
        return Response({
            'co': AttainmentSerializer(co_results, many=True).data,
            'po_pso': ProgramAttainmentSerializer(po_results, many=True).data,
        })
