from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Assessment, Student, StudentMark
from .serializers import AssessmentSerializer, StudentSerializer, StudentMarkSerializer


class AssessmentViewSet(viewsets.ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        course_id = self.request.query_params.get('course')
        return qs.filter(course_id=course_id) if course_id else qs


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        course_id = self.request.query_params.get('course')
        return qs.filter(course_id=course_id).order_by('roll_number') if course_id else qs.order_by('roll_number')


class StudentMarkViewSet(viewsets.ModelViewSet):
    """Supports bulk entry: POST a list of mark objects to save a whole class's marks at once."""
    queryset = StudentMark.objects.all()
    serializer_class = StudentMarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        assessment_id = self.request.query_params.get('assessment')
        return qs.filter(assessment_id=assessment_id) if assessment_id else qs

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            saved = self._upsert_marks(serializer.validated_data)
            return Response(StudentMarkSerializer(saved, many=True).data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

    def _upsert_marks(self, rows):
        saved = []
        with transaction.atomic():
            for row in rows:
                obj, _ = StudentMark.objects.update_or_create(
                    assessment=row['assessment'],
                    student=row['student'],
                    course_outcome=row.get('course_outcome'),
                    defaults={'marks_obtained': row['marks_obtained']},
                )
                saved.append(obj)
        return saved
