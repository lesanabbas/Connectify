from .models import Notification

def create_notification(user, message):

    notification = Notification.objects.create(
        user=user,
        message=message,
        is_read=False
    )
    return notification
