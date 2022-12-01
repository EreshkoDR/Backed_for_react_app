import os

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from recipes.validators import validate_min_value
from users.models import User


class Tag(models.Model):
    COLORS_CHOISES = [
        ('#F5825B', _('Кораловый')),
        ('#E15DFC', _('Розовый')),
        ('#618FE6', _('Синий')),
        ('#5DFCA7', _('Аквамирин')),
        ('#EFF576', _('Желтый')),
    ]
    name = models.CharField(
        _('Имя тега'),
        max_length=25,
        unique=True
    )
    color = models.CharField(
        _('Hex-код цвета'),
        max_length=8,
        choices=COLORS_CHOISES
    )
    slug = models.SlugField(
        _('Слаг тега'),
        unique=True
    )

    class Meta:
        verbose_name = _('Список тегов')
        verbose_name_plural = _('Список тегов')

    def __str__(self):
        return _('Tег') + f': {self.name}'


class Ingredient(models.Model):
    name = models.CharField(
        _('Название ингредиента'),
        max_length=100,
    )
    measurement_unit = models.CharField(
        _('Единицы измерения'),
        max_length=10
    )

    class Meta:
        verbose_name = _('Список ингредиентов')
        verbose_name_plural = _('Список ингредиентов')

    def __str__(self):
        return _('Ингредиент') + f': {self.name}'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name=_('Теги'))
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор')
    )
    ingredients = models.ManyToManyField(
        'IngredientRecipe',
        related_name='recipes',
        verbose_name=_('Ингредиенты')
    )
    name = models.CharField(
        _('Название рецепта'),
        max_length=200,
    )
    image = models.ImageField(
        _('Изображение рецепта'),
        upload_to='recipes',
    )
    text = models.TextField(
        _('Описание рецепта'),
    )
    cooking_time = models.IntegerField(
        _('Время приготовления в минутах'),
        validators=[validate_min_value],
    )
    create = models.DateTimeField(
        _('Дата создания рецепта'),
        auto_now=True,
    )

    class Meta:
        verbose_name = _('Список рецептов')
        verbose_name_plural = _('Список рецептов')

    def __str__(self):
        return _('Рецепт') + f': {self.name}'


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientrecipes'
    )
    amount = models.IntegerField(validators=[validate_min_value])


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriterecipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriterecipes',
    )

    class Meta:
        verbose_name = _('Список избранных рецептов')
        verbose_name_plural = _('Список избранных рецептов')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return (
            _('Подписка пользователя') + f': {self.user} '
            + _('на рецепт') + f': {self.recipe}')


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
    )   
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts'
    )

    class Meta:
        verbose_name = _('Список покупок')
        verbose_name_plural = _('Список покупок')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shopping_cart'
            )
        ]

    def __str__(self):
        return _('Список покупок пользователя') + f': {self.user}'
