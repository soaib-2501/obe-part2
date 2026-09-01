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
        {'name': 'T-1', 'term': 'Exam: T1', 'assessment_type': 'T1', 'questions': deepcopy(questions)},
        {'name': 'T-2', 'term': 'Exam: T2', 'assessment_type': 'T2', 'questions': deepcopy(questions)},
        {'name': 'T-3', 'term': 'Exam: T3', 'assessment_type': 'T3', 'questions': deepcopy(questions)},
    ]


TOOL_META = {
    'T1': ('T-1', 'Exam: T1'),
    'T2': ('T-2', 'Exam: T2'),
    'T3': ('T-3', 'Exam: T3'),
    'TA': ('TA', 'TA Marks'),
    'FEEDBACK': ('Feedback', 'Course Exit Feedback'),
}


def _co_for_question(question, outcomes):
    if question.course_outcome_id and question.course_outcome_id in outcomes:
        return outcomes[question.course_outcome_id]
    blob = f'{question.label or ""} {question.key or ""}'.lower()
    for co in outcomes.values():
        code = (co.co_code or '').strip().lower()
        if code and code in blob:
            return co
    return None


def tools_from_assessments(course):
    """Build Assessment Tools rows from Students & Marks question/CO mapping."""
    from assessments.models import Assessment, SHEET_TYPES
    outcomes = {o.id: o for o in course.outcomes.all().order_by('order', 'id')}
    tools = []
    for typ in SHEET_TYPES:
        assessment = (
            Assessment.objects.filter(course=course, assessment_type=typ)
            .prefetch_related('questions')
            .order_by('id')
            .first()
        )
        if not assessment:
            continue
        questions = []
        for i, q in enumerate(assessment.questions.all().order_by('order', 'id')):
            co = _co_for_question(q, outcomes)
            questions.append({
                'qno': q.label or q.key or f'Q{i + 1}',
                'co_code': co.co_code if co else '',
                'ques_level': question_level_for(co.cognitive_level if co else ''),
                'remarks': '',
                'max_marks': str(q.max_marks) if q.max_marks is not None else '',
                'source_key': q.key or '',
            })
        if not questions:
            continue
        name, default_term = TOOL_META[typ]
        tools.append({
            'name': name,
            'term': assessment.exam_label or default_term,
            'assessment_type': typ,
            'questions': questions,
        })
    return tools


def merge_synced_tools(generated, existing):
    old = {}
    extras = []
    known_types = set(TOOL_META)
    known_names = {meta[0] for meta in TOOL_META.values()}
    for tool in existing or []:
        typ = tool.get('assessment_type')
        name = tool.get('name')
        if typ in known_types or name in known_names:
            for q in tool.get('questions') or []:
                key = (typ or name, q.get('source_key') or q.get('qno'))
                old[key] = q
        else:
            extras.append(tool)
    merged = []
    for tool in generated:
        questions = []
        for q in tool['questions']:
            prev = old.get((tool['assessment_type'], q.get('source_key'))) or old.get((tool['name'], q.get('qno')))
            remarks = (prev or {}).get('remarks') or ''
            questions.append({ **q, 'remarks': remarks })
        merged.append({ **tool, 'questions': questions })
    merged.extend(extras)
    return merged


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
