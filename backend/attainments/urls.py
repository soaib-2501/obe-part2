from rest_framework.routers import DefaultRouter
from .views import AttainmentViewSet

router = DefaultRouter()
router.register('', AttainmentViewSet, basename='attainment')

urlpatterns = router.urls
