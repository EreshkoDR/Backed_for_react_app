from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        _('Название ингредиента'),
        max_length=200
    )
    amout = models.CharField(
        _('Количество'),
        max_length=6
        # Возможно нужно будет изменить на Float
    )
    measurement_unit = models.CharField(
        _('Единицы измерения'),
        max_length=7
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиеты')


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        _('Название тега'),
        max_length=30
    )
    hex_code = models.CharField(
        _('HEX код цвета'),
        max_length=7,
    )
    slug = models.SlugField(
        _('Слаг тэга'),
        unique=True
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')


class Recipe(models.Model):
    """Модель рецептов"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name=_('Автор рецепта')
    )
    name = models.CharField(
        _('Название рецепта'),
        max_length=200
    )
    picture = models.ImageField(
        upload_to='recipe/'
    )
    description = models.TextField(
        _('Описание рецепта'),
        help_text=_('Начните писать рецепт')
        # help_text=randome_choise_for_help_text
    )
    ingredient = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recieps',
        verbose_name=_('Тег рецепта')
    )
    cooking_time = models.IntegerField(
        _('Время приготовления'),
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
