from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['username'], name='username_idx'),
        ]

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def can_send_another_request(self):
        last_rejected = FriendRequest.objects.filter(from_user=self.from_user, to_user=self.to_user, is_accepted=False).last()
        if last_rejected and (timezone.now() - last_rejected.created_at) < timedelta(hours=24):
            return False
        return True
    

class UserBlock(models.Model):
    blocker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocking')
    blocked = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blocked')
    blocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')  # Prevent multiple blocks between same users

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"


class Activity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='target_user', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)