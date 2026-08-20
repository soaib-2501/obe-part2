from django.db import models
from courses.models import Course, CourseOutcome


class Attainment(models.Model):
    """
    SRS 'Attainments' table: Attainment_ID · Course_ID · CO_Attainment · PO_Attainment · PSO_Attainment.
    Stored per Course Outcome so PO/PSO attainment can be derived from the CO-PO-PSO mapping.
    direct/indirect follow the standard OBE formula:
      direct = 60% test average + 20% assignment average
      indirect = 20% course-exit-feedback average
      final = direct + indirect
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attainments')
    course_outcome = models.OneToOneField(CourseOutcome, on_delete=models.CASCADE, related_name='attainment')

    direct_attainment = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    indirect_attainment = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    final_attainment = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    attainment_level = models.PositiveSmallIntegerField(null=True, blank=True)  # 0-3 scale

    calculated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.course_outcome.co_code} = {self.final_attainment}'
