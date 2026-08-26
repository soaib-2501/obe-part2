from django.urls import path
from .views import OpeningReportDetailView

urlpatterns = [
    path('<int:course_id>/', OpeningReportDetailView.as_view(), name='opening-report'),
]
