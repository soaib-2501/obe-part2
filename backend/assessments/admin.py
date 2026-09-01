from django.contrib import admin
from .models import Assessment, AssessmentQuestion, Student, StudentMark, GradeBand

admin.site.register(Assessment)
admin.site.register(AssessmentQuestion)
admin.site.register(Student)
admin.site.register(StudentMark)
admin.site.register(GradeBand)
