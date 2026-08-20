from rest_framework import viewsets, permissions
from .models import Course, CourseOutcome, CoPoMapping
from .serializers import CourseSerializer, CourseOutcomeSerializer, CoPoMappingSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    Full CRUD on courses. Faculty see their own courses; Admins see everything
    (SRS 2.3: Faculty "manage course-related information", Admin has full access).
    """
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        qs = Course.objects.all()
        if user.is_faculty_role:
            qs = qs.filter(faculty=user)
        return qs

    def perform_create(self, serializer):
        if self.request.user.is_faculty_role:
            serializer.save(faculty=self.request.user)
        else:
            serializer.save()

    def perform_update(self, serializer):
        if self.request.user.is_faculty_role:
            serializer.save(faculty=self.request.user)
        else:
            serializer.save()


class CourseOutcomeViewSet(viewsets.ModelViewSet):
    queryset = CourseOutcome.objects.all()
    serializer_class = CourseOutcomeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        course_id = self.request.query_params.get('course')
        if course_id:
            qs = qs.filter(course_id=course_id)
        return qs


class CoPoMappingViewSet(viewsets.ModelViewSet):
    queryset = CoPoMapping.objects.all()
    serializer_class = CoPoMappingSerializer
    permission_classes = [permissions.IsAuthenticated]
