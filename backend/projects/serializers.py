from rest_framework import serializers
from .models import Project


class ProjectSerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source='course.course_code', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'course', 'course_code', 'course_name', 'project_title',
            'student_names', 'evaluation_status', 'marks_obtained', 'remarks',
        ]
