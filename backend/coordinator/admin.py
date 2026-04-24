from django.contrib import admin
from .models import CoordinatorProfile

@admin.register(CoordinatorProfile)
class CoordinatorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_select_related = ('user',)
    search_fields = ('user__email',)
