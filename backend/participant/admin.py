from django.contrib import admin

from .models import ParticipantProfile, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ParticipantProfile)
class ParticipantProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'experience')
    search_fields = ('user__email', 'college')
    filter_horizontal = ('skills',)
