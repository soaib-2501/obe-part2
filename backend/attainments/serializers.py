from rest_framework import serializers
from .models import Attainment, ProgramAttainment


class AttainmentSerializer(serializers.ModelSerializer):
    co_code = serializers.CharField(source='course_outcome.co_code', read_only=True)

    class Meta:
        model = Attainment
        fields = [
            'id', 'course', 'course_outcome', 'co_code',
            'direct_attainment', 'indirect_attainment', 'final_attainment',
            'attainment_level', 'calculated_at',
        ]
        read_only_fields = ['direct_attainment', 'indirect_attainment', 'final_attainment', 'attainment_level']


class ProgramAttainmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramAttainment
        fields = ['id', 'course', 'po_key', 'percentage', 'attainment_level', 'calculated_at']
        read_only_fields = ['percentage', 'attainment_level']


class AttainmentSerializer(serializers.ModelSerializer):
    co_code = serializers.CharField(source='course_outcome.co_code', read_only=True)

    class Meta:
        model = Attainment
        fields = [
            'id', 'course', 'course_outcome', 'co_code',
            'direct_attainment', 'indirect_attainment', 'final_attainment',
            'attainment_level', 'calculated_at',
        ]
        read_only_fields = ['direct_attainment', 'indirect_attainment', 'final_attainment', 'attainment_level']
