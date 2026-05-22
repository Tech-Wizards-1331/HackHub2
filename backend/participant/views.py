from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Count, Case, When, F, Value, BooleanField
from organizer.models import Hackathon, ProblemStatement
from .models import Team, TeamMember
from .forms import TeamRegistrationForm, TeamMemberForm
from .services import generate_team_qr_code

class HackathonListView(LoginRequiredMixin, ListView):
    model = Hackathon
    template_name = 'participant/hackathon_list.html'
    context_object_name = 'hackathons'
    paginate_by = 12  # Limit to 12 per page to keep render times fast

    def get_queryset(self):
        return (
            Hackathon.objects
            .filter(status='registration_open')
            .defer('room_configuration', 'seating_allocation', 'description')
            .order_by('start_date')
        )

class HackathonRegisterWizardView(LoginRequiredMixin, View):
    def get(self, request, pk):
        hackathon = get_object_or_404(Hackathon, pk=pk)
        
        if hackathon.status != 'registration_open':
            messages.error(request, "This hackathon is not open for registration.")
            return redirect('hackathon-list')

        # Find if user already has a draft team for this hackathon
        team = Team.objects.filter(leader=request.user, hackathon=hackathon).first()
        
        if team and team.is_registered:
            messages.info(request, "You have already registered a team for this hackathon.")
            return redirect('dashboard')
            
        # Check if user is already a member of another registered team
        if TeamMember.objects.filter(
            email=request.user.email,
            team__hackathon=hackathon,
            team__is_registered=True
        ).select_related('team', 'team__hackathon').exists():
            messages.info(request, "You are already registered as a member of a team for this hackathon.")
            return redirect('dashboard')
        
        team_form = TeamRegistrationForm(instance=team)
        member_form = TeamMemberForm()

        return render(request, 'participant/hackathon_register.html', {
            'hackathon': hackathon,
            'team_form': team_form,
            'member_form': member_form,
            'team': team,
        })

    def post(self, request, pk):
        hackathon = get_object_or_404(Hackathon, pk=pk)
        
        if hackathon.status != 'registration_open':
            messages.error(request, "This hackathon is not open for registration.")
            return redirect('hackathon-list')

        team = Team.objects.filter(leader=request.user, hackathon=hackathon).first()

        if team and team.is_registered:
            messages.info(request, "You have already registered a team for this hackathon.")
            return redirect('dashboard')
            
        if TeamMember.objects.filter(
            email=request.user.email,
            team__hackathon=hackathon,
            team__is_registered=True
        ).select_related('team').exists():
            messages.info(request, "You are already registered as a member of a team for this hackathon.")
            return redirect('dashboard')

        if 'save_team' in request.POST:
            team_form = TeamRegistrationForm(request.POST, instance=team)
            if team_form.is_valid():
                team = team_form.save(commit=False)
                team.hackathon = hackathon
                team.leader = request.user
                team.is_registered = False
                team.save()
                messages.success(request, "Team name saved.")
                return redirect('hackathon-register', pk=pk)
        elif 'add_member' in request.POST:
            if not team:
                messages.error(request, "Please save team name first.")
                return redirect('hackathon-register', pk=pk)
            member_form = TeamMemberForm(request.POST)
            if member_form.is_valid():
                member = member_form.save(commit=False)
                member.team = team
                try:
                    member.clean() # triggers email uniqueness check
                    member.save()
                    member_form.save_m2m() # for skills
                    messages.success(request, "Member added successfully.")
                except Exception as e:
                    messages.error(request, str(e))
                return redirect('hackathon-register', pk=pk)
            else:
                messages.error(request, "Failed to add member. Please check fields.")
        elif 'complete_registration' in request.POST:
            if not team:
                messages.error(request, "Team does not exist.")
                return redirect('hackathon-register', pk=pk)
            
            member_count = team.members.count() + 1 # +1 for leader
            if member_count < hackathon.min_team_size:
                messages.error(request, f"Validation Failed: Minimum team size is {hackathon.min_team_size} (Leader + {hackathon.min_team_size - 1} members). Currently you have {member_count}.")
                return redirect('hackathon-register', pk=pk)
            elif member_count > hackathon.max_team_size:
                messages.error(request, f"Validation Failed: Maximum team size is {hackathon.max_team_size}.")
                return redirect('hackathon-register', pk=pk)
            
            # Additional validation: all members must have required fields
            members = team.members.all()
            for member in members:
                if not member.college or not member.semester or not member.degree:
                    messages.error(request, f"Validation Failed: Member {member.name} is missing required profile fields.")
                    return redirect('hackathon-register', pk=pk)
            
            team.is_registered = True
            team.save()
            
            # Generate QR code for the team
            generate_team_qr_code(team)
            
            messages.success(request, "Registration complete!")
            return redirect('dashboard') # participant dashboard
        
        elif 'remove_member' in request.POST:
            member_id = request.POST.get('member_id')
            if team and member_id:
                TeamMember.objects.filter(id=member_id, team=team).delete()
                messages.success(request, "Member removed.")
            return redirect('hackathon-register', pk=pk)

        return redirect('hackathon-register', pk=pk)


class ParticipantHackathonHubView(LoginRequiredMixin, View):
    """
    Per-hackathon hub for a registered participant.
    Shows: hackathon info, team details, PS selection, and seating assignment.
    PS list uses the same cache-aside key as the REST API so cache is shared.
    PS selection is delegated to the REST API via JS fetch (concurrency-safe).
    """

    def _get_team(self, hackathon, user):
        """Return the team where the user is leader OR a member, for this hackathon."""
        team = Team.objects.filter(leader=user, hackathon=hackathon).first()
        if not team:
            member = TeamMember.objects.filter(
                email=user.email, team__hackathon=hackathon, team__is_registered=True
            ).select_related('team').first()
            if member:
                team = member.team
        return team

    def _get_problem_statements(self, hackathon):
        """Cache-aside: same key as REST API so both share the same cache entry."""
        cache_key = f"problem_statements_list_{hackathon.id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached, True  # (data, from_cache)

        ps_qs = (
            ProblemStatement.objects
            .filter(hackathon=hackathon, is_active=True)
            .annotate(
                current_teams_count=Count('selected_by_teams'),
                is_full=Case(
                    When(current_teams_count__gte=F('max_teams_allowed'), then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            )
            .order_by('-created_at')
        )
        # Return queryset directly (template renders it); REST API serializes to JSON
        return ps_qs, False

    def _get_team_seating(self, hackathon, team):
        """Extract this team's seating rows from hackathon.seating_allocation."""
        if not hackathon.seating_allocation or not team:
            return None
        allocation = hackathon.seating_allocation
        if not isinstance(allocation, dict):
            return None
        for entry in allocation.get('teams', []):
            if entry.get('name', '').strip().lower() == team.name.strip().lower():
                return entry
        return None

    def get(self, request, pk):
        hackathon = get_object_or_404(Hackathon, pk=pk)
        team = self._get_team(hackathon, request.user)

        if not team:
            messages.error(request, "You are not registered for this hackathon.")
            return redirect('dashboard')

        ps_data, from_cache = self._get_problem_statements(hackathon)
        team_seating = self._get_team_seating(hackathon, team)
        # prefetch_related for skills avoids N+1 per member
        members = team.members.prefetch_related('skills').exclude(email=team.leader.email)
        is_leader = (team.leader == request.user)

        return render(request, 'participant/hackathon_hub.html', {
            'hackathon': hackathon,
            'team': team,
            'members': members,
            'is_leader': is_leader,
            'problem_statements': ps_data,
            'team_seating': team_seating,
        })


class ParticipantTeamPassView(LoginRequiredMixin, View):
    """
    Dedicated mobile-optimized Team Pass page showing the team's QR code.
    Accessible by team leaders and team members.
    """

    def _get_team(self, hackathon, user):
        """Return the team where the user is leader OR a member."""
        team = Team.objects.filter(leader=user, hackathon=hackathon, is_registered=True).first()
        if not team:
            member = TeamMember.objects.filter(
                email=user.email, team__hackathon=hackathon, team__is_registered=True
            ).select_related('team').first()
            if member:
                team = member.team
        return team

    def get(self, request, pk):
        hackathon = get_object_or_404(Hackathon, pk=pk)
        team = self._get_team(hackathon, request.user)

        if not team:
            messages.error(request, "You are not registered for this hackathon.")
            return redirect('dashboard')

        # Ensure QR code exists (generate if missing)
        if not team.qr_token or not team.qr_code:
            generate_team_qr_code(team)
            team.refresh_from_db()

        members = team.members.prefetch_related('skills').exclude(email=team.leader.email)

        return render(request, 'participant/team_pass.html', {
            'hackathon': hackathon,
            'team': team,
            'members': members,
        })
