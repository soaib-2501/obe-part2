from rest_framework.routers import DefaultRouter
from .views import AssessmentViewSet, StudentViewSet, StudentMarkViewSet

router = DefaultRouter()
router.register('students', StudentViewSet, basename='student')
router.register('marks', StudentMarkViewSet, basename='student-mark')
router.register('', AssessmentViewSet, basename='assessment')

urlpatterns = router.urls
