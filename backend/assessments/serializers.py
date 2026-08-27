from rest_framework import serializers
from courses.access import faculty_owns_course
from .models import Assessment, Student, StudentMark


def _owned_course(user, course):
    if user and not faculty_owns_course(user, course):
        raise serializers.ValidationError('You can only use your own course offerings.')
    return course


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = ['id', 'course', 'assessment_type', 'max_marks']

    def validate_course(self, course):
        request = self.context.get('request')
        return _owned_course(getattr(request, 'user', None), course)


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'roll_number', 'name', 'course']

    def validate_course(self, course):
        request = self.context.get('request')
        return _owned_course(getattr(request, 'user', None), course)


class StudentMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentMark
        fields = ['id', 'assessment', 'student', 'course_outcome', 'marks_obtained']
        # UniqueTogether is enforced by update_or_create on bulk save, not by rejecting existing rows.
        validators = []

    def validate(self, attrs):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        assessment = attrs.get('assessment') or getattr(self.instance, 'assessment', None)
        student = attrs.get('student') or getattr(self.instance, 'student', None)
        outcome = attrs.get('course_outcome', getattr(self.instance, 'course_outcome', None))
        if assessment:
            _owned_course(user, assessment.course)
        if student:
            _owned_course(user, student.course)
        if assessment and student and student.course_id != assessment.course_id:
            raise serializers.ValidationError('Student and assessment must belong to the same course.')
        if outcome and assessment and outcome.course_id != assessment.course_id:
            raise serializers.ValidationError('Course outcome must belong to the same course.')
        return attrs
