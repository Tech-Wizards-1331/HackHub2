from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Hackathon, HackathonCoordinator, OrganizerProfile, ProblemStatement
from .api_serializers import (
    HackathonSerializer,
    HackathonCoordinatorSerializer,
    ProblemStatementSerializer,
)
from .permissions import (
    IsOrganizer,
    IsOrganizerOrReadOnlyCoordinator,
    CanManageProblemStatements,
)

User = get_user_model()

# IsOrganizer is now imported from .permissions


class HackathonViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for a Sub-Admin's Hackathons.
    """
    serializer_class = HackathonSerializer
    permission_classes = [IsOrganizerOrReadOnlyCoordinator]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        # Return hackathons the user owns (organizer) or is assigned to (coordinator)
        return Hackathon.objects.filter(
            Q(organizer__user=self.request.user)
            | Q(coordinators__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        # Make sure the user has an OrganizerProfile
        profile, created = OrganizerProfile.objects.get_or_create(user=self.request.user)
        serializer.save(organizer=profile)

    @action(detail=True, methods=['post'], permission_classes=[IsOrganizer])
    def assign_coordinator(self, request, pk=None):
        hackathon = self.get_object()
        email = request.data.get('email')
        responsibilities = request.data.get('responsibilities', [])
        
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate responsibilities against the strict enum
        valid_resps = [c[0] for c in HackathonCoordinator.Responsibility.choices]
        for r in responsibilities:
            if r not in valid_resps:
                return Response(
                    {'error': f'Invalid responsibility: {r}. Valid values: {valid_resps}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Deduplicate while preserving order
        responsibilities = list(dict.fromkeys(responsibilities))
        
        is_new_user = False
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Create shell user
            user = User.objects.create(email=email, role=User.Role.COORDINATOR)
            user.set_unusable_password()
            user.save()
            is_new_user = True

        # Send invite email for every coordinator assignment (new or existing user)
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.urls import reverse
        from .tasks import send_coordinator_invite_email

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        try:
            invite_path = reverse('accept_invite', kwargs={'uidb64': uid, 'token': token})
            invite_url = request.build_absolute_uri(invite_path)

            # Dispatch the email asynchronously via Celery
            send_coordinator_invite_email.delay(
                email=email,
                hackathon_name=hackathon.name,
                invite_url=invite_url
            )
        except Exception as e:
            # Log errors but do not fail the assignment
            import logging
            logging.getLogger(__name__).error(f"Failed to queue invite email task for {email}: {e}")
        
        # Safe role assignment: do not overwrite higher-privilege roles
        if user.role not in [User.Role.ORGANIZER, User.Role.SUPER_ADMIN, User.Role.COORDINATOR]:
            user.role = User.Role.COORDINATOR
            user.save(update_fields=['role'])
            
        # Create scoped permission assignment
        assignment, created = HackathonCoordinator.objects.get_or_create(
            user=user, 
            hackathon=hackathon
        )
        
        # Always update responsibilities even if not created newly
        assignment.responsibilities = responsibilities
        assignment.save()
        
        if is_new_user:
            message = 'User successfully created and invited as coordinator.'
        elif not created:
            message = 'Updated responsibilities for existing coordinator.'
        else:
            message = 'User successfully assigned as coordinator.'

        serializer = HackathonCoordinatorSerializer(assignment)
        return Response({'message': message, 'assignment': serializer.data}, status=status.HTTP_201_CREATED if (created or is_new_user) else status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def list_coordinators(self, request, pk=None):
        hackathon = self.get_object()
        coordinators = HackathonCoordinator.objects.filter(hackathon=hackathon).select_related('user')
        serializer = HackathonCoordinatorSerializer(coordinators, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsOrganizer])
    def unassign_coordinator(self, request, pk=None):
        hackathon = self.get_object()
        email = request.data.get('email')
        
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        assignment = HackathonCoordinator.objects.filter(hackathon=hackathon, user__email=email).first()
        if not assignment:
            return Response({'error': 'Coordinator not found for this hackathon.'}, status=status.HTTP_404_NOT_FOUND)
            
        assignment.delete()
        return Response({'message': 'Coordinator unassigned successfully.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        hackathon = self.get_object()
        # Placeholder for analytics logic
        data = {
            'total_teams': 0,
            'total_participants': 0,
            'status': hackathon.status,
            'message': 'Analytics endpoint placeholder'
        }
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def notify_participants(self, request, pk=None):
        hackathon = self.get_object()
        message = request.data.get('message', f'Update from {hackathon.name}')
        # Log to console for now — will be replaced with email/SMS integration
        print(f"[NOTIFY] {hackathon.name}: {message}")
        return Response({'success': True, 'message': 'Notification logged (placeholder).'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def generate_results(self, request, pk=None):
        hackathon = self.get_object()
        
        # Placeholder for logic
        return Response({'success': True, 'message': 'Results generated (placeholder).'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def coordinator_dashboard(self, request):
        """Return the coordinator's assigned hackathons with responsibilities and stats."""
        if request.user.role != User.Role.COORDINATOR:
            return Response(
                {'error': 'Only coordinators can access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        assignments = (
            HackathonCoordinator.objects
            .filter(user=request.user)
            .select_related('hackathon')
        )
        data = []
        for assignment in assignments:
            h = assignment.hackathon
            data.append({
                'hackathon': HackathonSerializer(h).data,
                'responsibilities': assignment.responsibilities,
                'stats': {
                    'problem_statements_count': h.problem_statements.count(),
                },
            })
        return Response(data, status=status.HTTP_200_OK)


class ProblemStatementViewSet(viewsets.ModelViewSet):
    """
    CRUD for problem statements scoped to a hackathon.
    Organizers and coordinators with PROBLEM_STATEMENTS responsibility can access.
    URL: /api/organizer/hackathons/{hackathon_pk}/problem-statements/
    """
    serializer_class = ProblemStatementSerializer
    permission_classes = [CanManageProblemStatements]
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _get_hackathon(self):
        """Resolve hackathon ensuring the user owns or is assigned to it."""
        return get_object_or_404(
            Hackathon.objects.filter(
                Q(organizer__user=self.request.user)
                | Q(coordinators__user=self.request.user)
            ).distinct(),
            pk=self.kwargs['hackathon_pk'],
        )

    def get_queryset(self):
        return ProblemStatement.objects.filter(
            hackathon_id=self.kwargs['hackathon_pk'],
        ).filter(
            Q(hackathon__organizer__user=self.request.user)
            | Q(hackathon__coordinators__user=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        hackathon = self._get_hackathon()
        serializer.save(hackathon=hackathon)

    def perform_update(self, serializer):
        self._get_hackathon()
        serializer.save()
