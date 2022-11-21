from django.db import models

from .validators import validate_min_value
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        'Имя тега',
        max_length=25,
    )
    color = models.CharField(
        'Hex-код цвета',
        max_length=8
    )
    slug = models.SlugField(
        'Слаг тега',

    )


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=50,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=10
    )


class Recipe(models.Model):
    tags = models.ForeignKey(
        Tag,
        on_delete=models.SET_NULL
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='recipes/images/'
    )
    text = models.TextField(
        'Описание рецепта'
    )
    cooking_time = models.IntegerField(
        'Время приготовления в минутах',
        validators=[validate_min_value]
    )


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingerdient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.IntegerField(validators=[validate_min_value])
