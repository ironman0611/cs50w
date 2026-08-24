from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
    )


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(
        User,
        related_name="liked_posts",
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"
