from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Message(models.Model):

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    # 💬 TEXT MESSAGE
    content = models.TextField(blank=True, null=True)

    # 📷 IMAGE MESSAGE (for future upgrade)
    image = models.ImageField(
        upload_to='chat_images/',
        blank=True,
        null=True
    )

    # 👀 READ RECEIPT
    is_seen = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.content if self.content else "Image Message"