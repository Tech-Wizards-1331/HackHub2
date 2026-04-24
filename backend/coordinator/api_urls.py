from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CoordinatorDashboardViewSet

router = DefaultRouter()
router.register(r'', CoordinatorDashboardViewSet, basename='coordinator')

urlpatterns = [
    path('', include(router.urls)),
]
