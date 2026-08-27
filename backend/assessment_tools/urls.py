from django.urls import path
from .views import AssessmentToolsDetailView

urlpatterns = [
    path('<int:course_id>/', AssessmentToolsDetailView.as_view(), name='assessment-tools'),
]
