"""
The attainment calculation engine (SRS 3.6).
Kept as a plain function — not a view — so it can be unit-tested and reused
(e.g. from a management command or a Celery task later) without touching HTTP.
"""
from decimal import Decimal
from courses.models import CourseOutcome, CoPoMapping
from assessments.models import StudentMark
from .models import Attainment, ProgramAttainment

TEST_TYPES = ['T1', 'T2', 'T3']
PO_KEYS = ['PO1', 'PO2', 'PO3', 'PSO1', 'PSO2']


def level_from_percentage(pct):
    if pct is None:
        return None
    if pct >= 70:
        return 3
    if pct >= 60:
        return 2
    if pct >= 50:
        return 1
    return 0


def calculate_for_course_outcome(course_outcome: CourseOutcome) -> Attainment:
    marks = StudentMark.objects.filter(course_outcome=course_outcome).select_related('assessment')

    test_marks = marks.filter(assessment__assessment_type__in=TEST_TYPES)
    assignment_marks = marks.filter(assessment__assessment_type='ASSIGNMENT')
    feedback_marks = marks.filter(assessment__assessment_type='FEEDBACK')

    def avg_percentage(qs):
        rows = list(qs)
        if not rows:
            return None
        total_pct = Decimal('0')
        for row in rows:
            max_marks = row.assessment.max_marks or 1
            total_pct += (row.marks_obtained / Decimal(max_marks)) * 100
        return total_pct / len(rows)

    test_pct = avg_percentage(test_marks)
    assignment_pct = avg_percentage(assignment_marks)
    feedback_pct = avg_percentage(feedback_marks)

    direct = None
    if test_pct is not None or assignment_pct is not None:
        direct = (test_pct or Decimal('0')) * Decimal('0.6') + (assignment_pct or Decimal('0')) * Decimal('0.2')
        # scale back up since weights don't sum to 1 on their own — direct is out of 80, normalize to 100
        direct = direct / Decimal('0.8') if direct else direct

    indirect = feedback_pct * Decimal('0.2') / Decimal('1') if feedback_pct is not None else None
    final = (direct or Decimal('0')) + (indirect or Decimal('0')) if (direct or indirect) else None

    # attainment_level uses a 0-3 scale derived from the final percentage
    level = level_from_percentage(final)

    attainment, _ = Attainment.objects.update_or_create(
        course_outcome=course_outcome,
        defaults={
            'course': course_outcome.course,
            'direct_attainment': direct,
            'indirect_attainment': indirect,
            'final_attainment': final,
            'attainment_level': level,
        },
    )
    return attainment


def calculate_for_course(course_id):
    outcomes = CourseOutcome.objects.filter(course_id=course_id)
    co_results = [calculate_for_course_outcome(co) for co in outcomes]
    po_results = calculate_program_attainments(course_id)
    return co_results, po_results


def calculate_program_attainments(course_id):
    """
    Weighted average: for each PO/PSO, Σ(CO_final × mapping_level) / Σ(mapping_level).
    Mapping 0 or blank is ignored.
    """
    results = []
    for po_key in PO_KEYS:
        mappings = CoPoMapping.objects.filter(
            course_outcome__course_id=course_id,
            po_key=po_key,
            level__isnull=False,
            level__gt=0,
        ).select_related('course_outcome')
        weighted = Decimal('0')
        weight = Decimal('0')
        for mapping in mappings:
            try:
                att = mapping.course_outcome.attainment
            except Attainment.DoesNotExist:
                continue
            if att.final_attainment is None:
                continue
            level = Decimal(mapping.level)
            weighted += att.final_attainment * level
            weight += level
        percentage = (weighted / weight) if weight else None
        obj, _ = ProgramAttainment.objects.update_or_create(
            course_id=course_id,
            po_key=po_key,
            defaults={
                'percentage': percentage,
                'attainment_level': level_from_percentage(percentage),
            },
        )
        results.append(obj)
    return results
