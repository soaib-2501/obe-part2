from django.urls import path
from .views import (
    ClosingReportDetailView,
    ClosingReportLoadHistoryView,
    ClosingYearSnapshotView,
)

urlpatterns = [
    path('<int:course_id>/load-history/', ClosingReportLoadHistoryView.as_view(), name='closing-report-load-history'),
    path('<int:course_id>/snapshots/', ClosingYearSnapshotView.as_view(), name='closing-report-snapshots'),
    path('<int:course_id>/', ClosingReportDetailView.as_view(), name='closing-report'),
]
