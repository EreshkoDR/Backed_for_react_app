from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, 'Авторизированный пользователь'),
        (ADMIN, 'Администратор')
    ]
    role = models.CharField(
        'Польховательские роли',
        choices=ROLE_CHOICES,
        default=USER,
        max_length=15
    )


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )