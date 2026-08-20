from rest_framework import serializers
from django.db import transaction
from .models import Course, CourseOutcome, CoPoMapping


class CoPoMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoPoMapping
        fields = ['id', 'course_outcome', 'po_key', 'level']


class CourseOutcomeSerializer(serializers.ModelSerializer):
    mappings = CoPoMappingSerializer(many=True, required=False)

    class Meta:
        model = CourseOutcome
        fields = ['id', 'course', 'co_code', 'description', 'cognitive_level', 'order', 'mappings']

    def create(self, validated_data):
        mappings_data = validated_data.pop('mappings', [])
        co = CourseOutcome.objects.create(**validated_data)
        for m in mappings_data:
            CoPoMapping.objects.create(course_outcome=co, **m)
        return co

    def update(self, instance, validated_data):
        mappings_data = validated_data.pop('mappings', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if mappings_data is not None:
            instance.mappings.all().delete()
            for m in mappings_data:
                CoPoMapping.objects.create(course_outcome=instance, **m)
        return instance


class CourseSerializer(serializers.ModelSerializer):
    outcomes = CourseOutcomeSerializer(many=True, required=False)
    faculty_name = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'course_name', 'nba_code', 'semester', 'academic_year',
            'credits', 'faculty', 'faculty_name', 'outcomes', 'created_at',
        ]

    def get_faculty_name(self, obj):
        if not obj.faculty:
            return None
        return obj.faculty.get_full_name() or obj.faculty.username

    def create(self, validated_data):
        with transaction.atomic():
            outcomes_data = validated_data.pop('outcomes', [])
            course = Course.objects.create(**validated_data)
            for i, co_data in enumerate(outcomes_data):
                mappings_data = co_data.pop('mappings', [])
                co_data.pop('order', None)  # always use position in the list, ignore any client-sent order
                co = CourseOutcome.objects.create(course=course, order=i, **co_data)
                for m in mappings_data:
                    CoPoMapping.objects.create(course_outcome=co, **m)
            return course