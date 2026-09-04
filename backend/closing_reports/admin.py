from django.contrib import admin
from .models import ClosingReport, ClosingYearSnapshot


@admin.register(ClosingReport)
class ClosingReportAdmin(admin.ModelAdmin):
    list_display = ('course', 'updated_at')


@admin.register(ClosingYearSnapshot)
class ClosingYearSnapshotAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'academic_year', 'semester', 'source', 'updated_at')
    list_filter = ('source', 'semester')
    search_fields = ('course_code', 'nba_code', 'academic_year')
