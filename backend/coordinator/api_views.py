from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from organizer.models import HackathonCoordinator
from .permissions import IsCoordinator, CoordinatorPermissionMixin
from .api_serializers import CoordinatorDashboardSerializer

class CoordinatorDashboardViewSet(CoordinatorPermissionMixin, viewsets.GenericViewSet):
    permission_classes = [IsCoordinator]
    authentication_classes = [JWTAuthentication]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Task-oriented dashboard returning scoped hackathons & stats."""
        assignments = self.get_coordinator_assignments()
        
        hackathons = []
        for assignment in assignments:
            # Attach the assignment to the object to avoid re-querying in the serializer
            hackathon = assignment.hackathon
            hackathon.coordinator_assignment = assignment
            hackathons.append(hackathon)
            
        serializer = CoordinatorDashboardSerializer(hackathons, many=True, context={'request': request})
        return Response({'hackathons': serializer.data}, status=status.HTTP_200_OK)
