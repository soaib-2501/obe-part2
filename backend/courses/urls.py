from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, CourseOutcomeViewSet, CoPoMappingViewSet

router = DefaultRouter()
# Register the more specific paths FIRST — CourseViewSet is registered at '' (root),
# and its detail route (/<pk>/) would otherwise swallow /outcomes/ and /mappings/
# if it were registered before them.
router.register('outcomes', CourseOutcomeViewSet, basename='course-outcome')
router.register('mappings', CoPoMappingViewSet, basename='co-po-mapping')
router.register('', CourseViewSet, basename='course')

urlpatterns = router.urls
