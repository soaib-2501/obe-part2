from django.db import models
from courses.models import Course


class Assessment(models.Model):
    """SRS 'Assessments' table: Assessment_ID · Course_ID · Assessment_Type · Maximum_Marks."""
    class Type(models.TextChoices):
        T1 = 'T1', 'Test 1'
        T2 = 'T2', 'Test 2'
        T3 = 'T3', 'Test 3'
        ASSIGNMENT = 'ASSIGNMENT', 'Assignment'
        ATTENDANCE = 'ATTENDANCE', 'Attendance'
        PROJECT = 'PROJECT', 'Project'
        FEEDBACK = 'FEEDBACK', 'Course Exit Feedback'

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    assessment_type = models.CharField(max_length=12, choices=Type.choices)
    max_marks = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.course.course_code} — {self.assessment_type}'


class Student(models.Model):
    """Student on one course offering. Same roll can exist on another offering/session."""
    roll_number = models.CharField(max_length=30)
    name = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')

    class Meta:
        unique_together = ('course', 'roll_number')

    def __str__(self):
        return f'{self.roll_number} — {self.name}'


class StudentMark(models.Model):
    """Per-student, per-assessment, per-CO marks — the raw input the attainment engine reads."""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='marks')
    course_outcome = models.ForeignKey('courses.CourseOutcome', on_delete=models.CASCADE, related_name='marks', null=True, blank=True)
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('assessment', 'student', 'course_outcome')

    def __str__(self):
        return f'{self.student.roll_number} / {self.assessment} = {self.marks_obtained}'
