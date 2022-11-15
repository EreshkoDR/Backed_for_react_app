from django.db import models
from django.contrib.auth.models import AbstractUser


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