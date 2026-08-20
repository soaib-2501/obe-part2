from django.contrib import admin
from .models import Assessment, Student, StudentMark

admin.site.register(Assessment)
admin.site.register(Student)
admin.site.register(StudentMark)
