import json

from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from .models import Hackathon, ProblemStatement
from .forms import HackathonForm, ProblemStatementForm
from .services.seating import get_teams_for_allocation, allocate


class OrganizerMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Common mixin: user must be authenticated with organizer role."""
    def test_func(self):
        return getattr(self.request.user, 'role', None) == 'organizer'


class OrganizerDashboardView(OrganizerMixin, TemplateView):
    template_name = 'organizer/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.request.user, 'organizer_profile'):
            context['hackathons'] = Hackathon.objects.filter(
                organizer=self.request.user.organizer_profile
            ).order_by('-created_at')
        else:
            context['hackathons'] = []
        return context


class CreateHackathonView(OrganizerMixin, CreateView):
    model = Hackathon
    form_class = HackathonForm
    template_name = 'organizer/create_hackathon.html'
    success_url = reverse_lazy('organizer-dashboard')

    def form_valid(self, form):
        form.instance.organizer = self.request.user.organizer_profile
        messages.success(self.request, f'Hackathon "{form.instance.name}" created successfully!')
        return super().form_valid(form)


class HackathonDetailView(OrganizerMixin, DetailView):
    model = Hackathon
    template_name = 'organizer/hackathon_detail.html'
    context_object_name = 'hackathon'

    def test_func(self):
        if not super().test_func():
            return False
        hackathon = self.get_object()
        return hackathon.organizer.user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hackathon = self.get_object()
        context['problem_statements'] = hackathon.problem_statements.all()
        context['room_configuration_json'] = json.dumps(
            hackathon.room_configuration
        ) if hackathon.room_configuration else '[]'
        context['seating_allocation'] = hackathon.seating_allocation
        return context


class AddProblemStatementView(OrganizerMixin, CreateView):
    model = ProblemStatement
    form_class = ProblemStatementForm
    template_name = 'organizer/add_problem_statement.html'

    def test_func(self):
        if not super().test_func():
            return False
        hackathon = get_object_or_404(Hackathon, pk=self.kwargs['hackathon_id'])
        return hackathon.organizer.user == self.request.user

    def form_valid(self, form):
        hackathon = get_object_or_404(Hackathon, pk=self.kwargs['hackathon_id'])
        form.instance.hackathon = hackathon
        messages.success(self.request, f'Problem statement "{form.instance.title}" added.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('organizer-hackathon-detail', kwargs={'pk': self.kwargs['hackathon_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hackathon'] = get_object_or_404(Hackathon, pk=self.kwargs['hackathon_id'])
        return context


class DeleteProblemStatementView(OrganizerMixin, DeleteView):
    model = ProblemStatement

    def test_func(self):
        if not super().test_func():
            return False
        ps = self.get_object()
        return ps.hackathon.organizer.user == self.request.user

    def get_success_url(self):
        ps = self.get_object()
        messages.success(self.request, f'Problem statement "{ps.title}" deleted.')
        return reverse('organizer-hackathon-detail', kwargs={'pk': ps.hackathon.pk})

    # Skip confirmation template — POST-only delete
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


class RunSeatingAllocationView(OrganizerMixin, View):

    def post(self, request, hackathon_id):
        hackathon = get_object_or_404(Hackathon, pk=hackathon_id)
        if hackathon.organizer.user != request.user:
            messages.error(request, 'Permission denied.')
            return redirect('organizer-dashboard')

        raw_config = request.POST.get('room_configuration', '').strip()
        if not raw_config:
            messages.error(request, 'Room configuration cannot be empty.')
            return redirect('organizer-hackathon-detail', pk=hackathon_id)

        try:
            rooms_config = json.loads(raw_config)
        except json.JSONDecodeError as e:
            messages.error(request, f'Invalid JSON: {e}')
            return redirect('organizer-hackathon-detail', pk=hackathon_id)

        hackathon.room_configuration = rooms_config
        hackathon.save()

        teams = get_teams_for_allocation(hackathon_id)
        if not teams:
            messages.warning(request, 'No teams found for this hackathon. Room config saved but allocation skipped.')
            return redirect('organizer-hackathon-detail', pk=hackathon_id)

        allocation_result = allocate(teams, rooms_config)
        hackathon.seating_allocation = allocation_result
        hackathon.save()

        messages.success(request, 'Seating allocation completed successfully!')
        return redirect('organizer-hackathon-detail', pk=hackathon_id)
