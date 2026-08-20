from django.db import models
from courses.models import Course


class Project(models.Model):
    """SRS 'Projects' table: Project_ID · Project_Title · Evaluation_Status."""
    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Not Started'
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        EVALUATED = 'EVALUATED', 'Evaluated'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='projects')
    project_title = models.CharField(max_length=255)
    student_names = models.CharField(max_length=500, help_text='Comma-separated group members')
    evaluation_status = models.CharField(max_length=15, choices=Status.choices, default=Status.NOT_STARTED)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return self.project_title
