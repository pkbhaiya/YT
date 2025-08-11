from django.db import models
from django.contrib.auth.models import User

class UserAPIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    youtube_api_key = models.CharField(max_length=255)
    openai_api_key = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


