from rest_framework import viewsets, permissions
from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('course').all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_faculty_role:
            qs = qs.filter(course__faculty=user)
        course_id = self.request.query_params.get('course')
        status_filter = self.request.query_params.get('status')
        if course_id:
            qs = qs.filter(course_id=course_id)
        if status_filter:
            qs = qs.filter(evaluation_status=status_filter)
        return qs.order_by('evaluation_status', 'project_title')
