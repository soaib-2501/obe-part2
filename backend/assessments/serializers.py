from rest_framework import serializers
from .models import Assessment, Student, StudentMark


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['id', 'course', 'assessment_type', 'max_marks']


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'roll_number', 'name', 'course']


class StudentMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMark
        fields = ['id', 'assessment', 'student', 'course_outcome', 'marks_obtained']
        # UniqueTogether is enforced by update_or_create on bulk save, not by rejecting existing rows.
        validators = []
