from django.contrib import admin
from .models import Course, CourseOutcome, CoPoMapping, LectureModule, CourseBook

admin.site.register(Course)
admin.site.register(CourseOutcome)
admin.site.register(CoPoMapping)
admin.site.register(LectureModule)
admin.site.register(CourseBook)
