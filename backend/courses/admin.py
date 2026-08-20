from django.contrib import admin
from .models import Course, CourseOutcome, CoPoMapping

admin.site.register(Course)
admin.site.register(CourseOutcome)
admin.site.register(CoPoMapping)
