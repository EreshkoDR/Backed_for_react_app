from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (USER, _('Авторизированный пользователь')),
        (ADMIN, _('Администратор')),
    ]
    role = models.CharField(
        _('Пользовательские роли'),
        choices=ROLE_CHOICES,
        default=USER,
        max_length=15
    )

    class Meta:
        ordering = ['id']
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return _('Пользователь') + f': {self.username}'

    @property
    def is_admin(self) -> bool:
        return self.role == self.ADMIN


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

    class Meta:
        verbose_name = _('Список подписок')
        verbose_name_plural = _('Список подписок')
        constraints = [
            models.CheckConstraint(
                check=~models.Q(author=models.F('user')),
                name='author_exclude_user'
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return (
            _('Подписка пользователя') + f': {self.user} '
            + _('на') + f': {self.author}'
        )
