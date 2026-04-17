from django.contrib import admin

from .models import VolunteerProfile


@admin.register(VolunteerProfile)
class VolunteerProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__email',)
