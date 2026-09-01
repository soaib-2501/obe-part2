from rest_framework import serializers
from .models import AssessmentToolsDocument


class AssessmentToolsDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentToolsDocument
        fields = [
            'id', 'course', 'doc_title', 'sub_heading', 'semester_label',
            'module_coordinator', 'watermark_text', 'tools', 'updated_at',
        ]
        read_only_fields = ['id', 'course', 'updated_at']

    def validate_tools(self, value):
        if value in (None, ''):
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError('Tools must be a list.')
        cleaned = []
        for tool in value:
            if not isinstance(tool, dict):
                raise serializers.ValidationError('Each tool must be an object.')
            questions = tool.get('questions') or []
            if not isinstance(questions, list):
                raise serializers.ValidationError('Each tool needs a questions list.')
            cleaned.append({
                'name': str(tool.get('name') or '').strip() or 'T-1',
                'term': str(tool.get('term') or '').strip(),
                'assessment_type': str(tool.get('assessment_type') or '').strip(),
                'questions': [
                    {
                        'qno': str(q.get('qno') or '').strip() or f'Q{i + 1}',
                        'co_code': str(q.get('co_code') or '').strip(),
                        'ques_level': str(q.get('ques_level') or '').strip(),
                        'remarks': str(q.get('remarks') or ''),
                        'max_marks': str(q.get('max_marks') or '').strip(),
                        'source_key': str(q.get('source_key') or '').strip(),
                    }
                    for i, q in enumerate(questions)
                    if isinstance(q, dict)
                ],
            })
        return cleaned
