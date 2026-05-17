import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import ProblemStatement, Hackathon
from .api_serializers import ProblemStatementSerializer
from .services.seating import get_teams_for_allocation, allocate


class StandardResultsPagePagination(PageNumberPagination):
    """20 results per page; clients can request up to 100 via ?page_size=N."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsOrganizerPermission(permissions.BasePermission):
    """Only allow users with the 'organizer' role."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'organizer'
        )


class ProblemStatementViewSet(viewsets.ModelViewSet):
    """
    CRUD for problem statements scoped to hackathons owned by the
    authenticated organizer.

    - List / Retrieve: returns problem statements for the organizer's hackathons.
    - Create: requires `hackathon` in request body; validated against ownership.
    - Update / Delete: only the owning organizer can modify.
    """
    serializer_class = ProblemStatementSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizerPermission]
    pagination_class = StandardResultsPagePagination

    def get_queryset(self):
        return ProblemStatement.objects.filter(
            hackathon__organizer__user=self.request.user,
        )

    def perform_create(self, serializer):
        hackathon = serializer.validated_data['hackathon']
        if hackathon.organizer.user != self.request.user:
            raise PermissionDenied(
                "You can only add problem statements to your own hackathons."
            )
        serializer.save()

    def perform_update(self, serializer):
        hackathon = serializer.instance.hackathon
        if hackathon.organizer.user != self.request.user:
            raise PermissionDenied(
                "You can only edit problem statements for your own hackathons."
            )
        serializer.save()

    def perform_destroy(self, instance):
        if instance.hackathon.organizer.user != self.request.user:
            raise PermissionDenied(
                "You can only delete problem statements for your own hackathons."
            )
        instance.delete()


class AllocateSeatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizerPermission]

    def post(self, request, hackathon_id):
        hackathon = get_object_or_404(Hackathon, id=hackathon_id)
        if hackathon.organizer.user != request.user:
            raise PermissionDenied("You can only allocate seats for your own hackathons.")

        rooms_config = request.data.get('rooms_config')
        if rooms_config is not None:
            hackathon.room_configuration = rooms_config
            hackathon.save()
        else:
            rooms_config = hackathon.room_configuration

        if not rooms_config:
            return Response(
                {"error": "rooms_config must be provided or previously saved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        teams = get_teams_for_allocation(hackathon_id)
        if not teams:
            return Response(
                {"error": "No teams found for this hackathon."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Trigger the celery background task instead of synchronous allocation
        from .tasks import allocate_seats_task
        task = allocate_seats_task.delay(hackathon_id)

        return Response(
            {
                "message": "Seating allocation started in the background.",
                "task_id": task.id
            },
            status=status.HTTP_202_ACCEPTED
        )


class ExportSeatingCSVView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizerPermission]

    def get(self, request, hackathon_id):
        hackathon = get_object_or_404(Hackathon, id=hackathon_id)
        if hackathon.organizer.user != request.user:
            raise PermissionDenied("You can only export seats for your own hackathons.")

        allocation = hackathon.seating_allocation
        if not allocation or 'room_view' not in allocation:
            return Response(
                {"error": "No seating allocation found for this hackathon."},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="seating_export_{hackathon_id}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Room', 'Section', 'Row', 'Bench', 'Team', 'Member'])

        room_view = allocation['room_view']
        for room_no, room_data in room_view.items():
            for row_no, row_data in room_data.get('rows', {}).items():
                section = row_data.get('section', '')
                for bench in row_data.get('benches', []):
                    bench_no = bench.get('bench', '')
                    for assigned in bench.get('assigned', []):
                        writer.writerow([
                            room_no,
                            section,
                            row_no,
                            bench_no,
                            assigned.get('team', ''),
                            assigned.get('member', '')
                        ])

        return response
