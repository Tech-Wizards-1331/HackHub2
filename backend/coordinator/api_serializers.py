from rest_framework import serializers
from organizer.models import Hackathon, HackathonCoordinator

class CoordinatorDashboardSerializer(serializers.ModelSerializer):
    responsibilities = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Hackathon
        fields = ['id', 'name', 'status', 'registration_status', 'responsibilities', 'summary']
        
    def get_assignment(self, obj):
        user = self.context['request'].user
        # Cached assignment on the object if prefetched, otherwise query
        if hasattr(obj, 'coordinator_assignment'):
            return obj.coordinator_assignment
        return HackathonCoordinator.objects.filter(user=user, hackathon=obj).first()
        
    def get_responsibilities(self, obj):
        assignment = self.get_assignment(obj)
        return assignment.responsibilities if assignment else []
        
    def get_summary(self, obj):
        assignment = self.get_assignment(obj)
        resp = assignment.responsibilities if assignment else []
        
        summary = {}
        if 'problem_statements' in resp:
            summary['problem_statements'] = {
                'total': obj.problem_statements.count(),
                'active': obj.problem_statements.filter(is_active=True).count()
            }
        if 'analytics' in resp or 'teams' in resp:
            summary['teams'] = {
                'max_teams': obj.max_teams,
                'max_team_size': obj.max_team_size
            }
        return summary
