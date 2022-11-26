from django_filters import rest_framework
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    tags = rest_framework.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        label='Tags',
        field_name='tags__slug',
        to_field_name='slug'
    )

    is_favorited = rest_framework.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_is_favorited(self, queryset, param, value):
        user = self.request.user
        if value and user.is_authenticated:
            queryset = queryset.filter(favoriterecipes__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, param, value):
        user = self.request.user
        if value and user.is_authenticated:
            queryset = queryset.filter(carts__user=user)
        return queryset
