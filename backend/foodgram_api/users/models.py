from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, _('Авторизированный пользователь')),
        (ADMIN, _('Администратор'))
    ]

    role = models.CharField(
        _('Пользовательские роли'),
        choices=ROLE_CHOICES,
        default=USER,
        max_length=20,
    )
