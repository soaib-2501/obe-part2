from django.db import models
from django.conf import settings


class Course(models.Model):
    """SRS 'Courses' table: Course_ID · Course_Code · Course_Name · Semester · Credits."""
    class Semester(models.TextChoices):
        ODD = 'ODD', 'Odd'
        EVEN = 'EVEN', 'Even'

    course_code = models.CharField(max_length=30, unique=True)
    course_name = models.CharField(max_length=255)
    nba_code = models.CharField(max_length=20, blank=True)
    semester = models.CharField(max_length=6, choices=Semester.choices)
    academic_year = models.CharField(max_length=9, help_text='e.g. 2025-26')
    credits = models.PositiveSmallIntegerField(default=3)
    faculty = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='courses', limit_choices_to={'role': 'FACULTY'},
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course_code', 'academic_year')
        ordering = ['-academic_year', 'course_code']

    def __str__(self):
        return f'{self.course_code} — {self.course_name} ({self.academic_year})'


class CourseOutcome(models.Model):
    """SRS 'Course Outcomes' table: CO_ID · Course_ID · CO_Code · Description · Cognitive_Level."""
    class CognitiveLevel(models.TextChoices):
        REMEMBER = 'REMEMBER', 'Remember (C1)'
        UNDERSTAND = 'UNDERSTAND', 'Understand (C2)'
        APPLY = 'APPLY', 'Apply (C3)'
        ANALYZE = 'ANALYZE', 'Analyze (C4)'
        EVALUATE = 'EVALUATE', 'Evaluate (C5)'
        CREATE = 'CREATE', 'Create / Design (C6)'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='outcomes')
    co_code = models.CharField(max_length=20)  # e.g. "C110.1"
    description = models.TextField()
    cognitive_level = models.CharField(max_length=12, choices=CognitiveLevel.choices)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'co_code')

    def __str__(self):
        return self.co_code


class CoPoMapping(models.Model):
    """SRS 3.4 CO-PO-PSO Mapping Module — one row per (CourseOutcome x PO/PSO column)."""
    PO_CHOICES = [('PO1', 'PO1'), ('PO2', 'PO2'), ('PO3', 'PO3'), ('PSO1', 'PSO1'), ('PSO2', 'PSO2')]

    course_outcome = models.ForeignKey(CourseOutcome, on_delete=models.CASCADE, related_name='mappings')
    po_key = models.CharField(max_length=5, choices=PO_CHOICES)
    level = models.PositiveSmallIntegerField(null=True, blank=True)  # 0-3, null = blank cell

    class Meta:
        unique_together = ('course_outcome', 'po_key')

    def __str__(self):
        return f'{self.course_outcome.co_code} → {self.po_key} = {self.level}'
