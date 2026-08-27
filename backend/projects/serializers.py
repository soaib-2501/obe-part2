from rest_framework import serializers
from courses.access import faculty_owns_course
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

    def validate_course(self, course):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user and not faculty_owns_course(user, course):
            raise serializers.ValidationError('You can only add projects on your own courses.')
        return course
