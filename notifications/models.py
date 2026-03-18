from django.db import models
from accounts.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order_status', 'Order Status Update'),
        ('build_approval', 'Build Approval'),
        ('support', 'Support Ticket Update'),
        ('system', 'System Notification')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, null=True)  # Optional link to related content
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

    @classmethod
    def create_notification(cls, user, type, title, message, link=None):
        """Helper method to create notifications"""
        notification = cls.objects.create(
            user=user,
            type=type,
            title=title,
            message=message,
            link=link
        )
        return notification