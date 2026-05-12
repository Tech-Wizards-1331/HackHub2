from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .api_views import ProblemStatementViewSet, AllocateSeatsView, ExportSeatingCSVView

router = DefaultRouter()
router.register(r'problem-statements', ProblemStatementViewSet, basename='problemstatement')

urlpatterns = [
    path('', include(router.urls)),
    path('hackathons/<int:hackathon_id>/allocate-seats/', AllocateSeatsView.as_view(), name='allocate-seats'),
    path('hackathons/<int:hackathon_id>/seating-export/', ExportSeatingCSVView.as_view(), name='seating-export'),
]
