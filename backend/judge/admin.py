from django.contrib import admin

from .models import JudgeProfile


@admin.register(JudgeProfile)
class JudgeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise', 'years_of_experience')
    search_fields = ('user__email', 'expertise')
