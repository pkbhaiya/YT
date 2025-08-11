

from django.contrib import admin
from .models import UserAPIKey

@admin.register(UserAPIKey)
class UserAPIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'youtube_api_key', 'openai_api_key', 'created_at')
    search_fields = ('user__username',)

