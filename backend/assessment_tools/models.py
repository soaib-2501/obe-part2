from copy import deepcopy

from django.db import models
from courses.models import Course


QUESTION_LEVEL_FROM_CO = {
    'REMEMBER': 'Remember',
    'UNDERSTAND': 'Understand',
    'APPLY': 'Apply',
    'ANALYZE': 'Analyze',
    'EVALUATE': 'Evaluate',
    'CREATE': 'Design',
}


def question_level_for(cognitive_level):
    return QUESTION_LEVEL_FROM_CO.get(cognitive_level or '', 'Understand')


def default_questions(course):
    outcomes = list(course.outcomes.all().order_by('order', 'id'))
    if not outcomes:
        return [{'qno': 'Q1', 'co_code': '', 'ques_level': 'Understand', 'remarks': ''}]
    count = min(len(outcomes), 4)
    rows = []
    for i, co in enumerate(outcomes[:count]):
        rows.append({
            'qno': f'Q{i + 1}',
            'co_code': co.co_code,
            'ques_level': question_level_for(co.cognitive_level),
            'remarks': '',
        })
    return rows


def default_tools(course):
    questions = default_questions(course)
    return [
        {'name': 'T-1', 'questions': deepcopy(questions)},
        {'name': 'T-2', 'questions': deepcopy(questions)},
        {'name': 'T-3', 'questions': deepcopy(questions)},
    ]


class AssessmentToolsDocument(models.Model):
    """Third OBE document: question-wise CO mapping for one course offering."""
    course = models.OneToOneField(
        Course, on_delete=models.CASCADE, related_name='assessment_tools',
    )
    doc_title = models.CharField(max_length=255, default='Assessment Tools')
    sub_heading = models.CharField(
        max_length=255,
        default='Cognitive level mapping of CO to the assessment tool',
        blank=True,
    )
    semester_label = models.CharField(max_length=80, blank=True)
    module_coordinator = models.CharField(max_length=255, blank=True)
    watermark_text = models.CharField(max_length=80, default='ASSESSMENT')
    tools = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Assessment Tools — {self.course}'

    def apply_defaults(self):
        if not self.doc_title:
            self.doc_title = 'Assessment Tools'
        if not self.sub_heading:
            self.sub_heading = 'Cognitive level mapping of CO to the assessment tool'
        if not self.watermark_text:
            self.watermark_text = 'ASSESSMENT'
        if not self.semester_label:
            sem = 'Even' if self.course.semester == Course.Semester.EVEN else 'Odd'
            self.semester_label = f'{sem} Semester'
        if not self.tools:
            self.tools = default_tools(self.course)
