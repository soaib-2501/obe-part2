from rest_framework.routers import DefaultRouter
from .views import AssessmentViewSet, StudentViewSet, StudentMarkViewSet, GradeBandViewSet

router = DefaultRouter()
router.register('students', StudentViewSet, basename='student')
router.register('marks', StudentMarkViewSet, basename='student-mark')
router.register('grades', GradeBandViewSet, basename='grade-band')
router.register('', AssessmentViewSet, basename='assessment')

urlpatterns = router.urls
