import base64

from django.conf import settings
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import ValidationError

from .models import Ingredient, IngredientRecipe, Recipe, Tag
from users.models import User
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи модели `Recipe` и `Ingredient`.
    Завязана с моделью `IngredientRecipe`. Поля `name` и
    `measurement_unit` определяются по возвращенной модели `IngredientRecipe`.
    """
    id = serializers.ModelField(IngredientRecipe.ingredient.field)
    name = serializers.SerializerMethodField(read_only=True)
    measurement_unit = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, instance: IngredientRecipe):
        """
        Возврат значения для поля `name` из модели `IngredientRecipe`.
        """
        return instance.ingredient.name

    def get_measurement_unit(self, instance: IngredientRecipe):
        """
        Возврат значения для поля `measurement_unit` из модели
        `IngredientRecipe`.
        """
        return instance.ingredient.measurement_unit


class Base64ImageField(serializers.ImageField):
    """ Сериализатор для декодирования изображения из `base64` в файл."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели `Recipe`."""
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='check_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='check_is_in_shopping_cart'
    )
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = (
            'id', 'author', 'is_favorited', 'is_in_shopping_cart',

        )

    def validate_ingredients(self, values):
        ingredient = Ingredient.objects.all()
        for value in values:
            id = value.get('id')
            amount = value.get('amount')
            if not ingredient.filter(id=id).exists():
                raise ValidationError(f'Ingredient with id: {id} isn`t exist')
            if isinstance(amount, int):
                if amount <= 0:
                    raise ValidationError(
                        'Field `amount` must be great than zero'
                    )
            else:
                raise ValidationError('Field `amount` must be `int`')
        return values

    def check_is_favorited(self, instance) -> bool:
        """
        Булевая функция возвращающая `True` если рецепт находится в
        списке избранных.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            recipe = instance
            return user.favoriterecipes.filter(recipe=recipe).exists()
        return False

    def check_is_in_shopping_cart(self, instance) -> bool:
        """
        Булевая функция возвращающая `True` если рецепт находится в
        списке покупок.
        """
        user = self.context['request'].user
        if user.is_authenticated:
            recipe = instance
            return user.carts.filter(recipe=recipe).exists()
        return False

    def add_ingredient_to_recipe(self, ingredients):
        """
        Функция добавляющая игредиент и его колличество в промежуточную
        таблицу `IngredientRecipe` и возвращает объект(ы) этой модели.
        """
        bulk = []
        for data in ingredients:
            data = {
                'ingredient': Ingredient.objects.get(id=data.get('id')),
                'amount': data.get('amount')
            }
            bulk.append(IngredientRecipe(**data))
        return IngredientRecipe.objects.bulk_create(bulk)

    def create(self, validated_data):
        """
        ## Функция создания рецепта.
        Принимает валидированные данные. Создает объект модели `Recipe`,
        затем создает модели ингредиентов через функцию
        `addadd_ingredient_to_recipe()' в которую помещаются валидированные
        данные из поля `ingredients`.
        После к экземпляру модели `Recipe` добавляются теги и ингредиенты.
        Возвращает экземпляр объекта `Recipe`.
        """
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context['request'].user
        validated_data['author'] = author
        recipe = Recipe.objects.create(**validated_data)
        ingredients = self.add_ingredient_to_recipe(ingredients)
        recipe.tags.add(*tags)
        recipe.ingredients.add(*ingredients)
        return recipe

    def update(self, instance: Recipe, validated_data):
        """
        ### Функция обновления рецепта.
        Принимает экземпляр модели `Recipe` и валидированные данные.
        Через `try - except` проверяет валидированные данные на наличие
        данных с полей `ingredients` и `tags`. При из наличии обновляет
        таблицы.
        """
        recipe = instance
        try:
            ingredients = validated_data.pop('ingredients')
            ingredients: list = self.add_ingredient_to_recipe(ingredients)
            recipe.ingredients.set(ingredients)
        except KeyError:
            pass
        try:
            tags: list = validated_data.pop('tags')
            recipe.tags.set(tags)
        except KeyError:
            pass
        return super().update(recipe, validated_data)


class ResipeFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    """Сериализатор рецептов авторов, на которых подписан пользователь."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed', 'recipes',
                  'recipes_count')

    def get_recipes(self, user, *args, **kwargs):
        """
        Фильтрующая функция. Ограничивает число объектов поля `recipes`
        через параметр запроса `recipes_limit`.
        """
        request = self.context['request']
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is None or not isinstance(recipes_limit, int):
            recipes_limit = settings.LIMIT_RECIPES
        queryset = user.recipes.all()[:int(recipes_limit)]
        return ResipeFavoriteSerializer(queryset, many=True).data

    def get_recipes_count(self, user):
        return Recipe.objects.filter(author=user).count()
