from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, mixins

from .models import Ingredient, Recipe, Tag
from .serializers import (IngredientRecipeSerializer, IngredientSerializer,
                          RecipeSerializer, ResipeFavoriteSerializer,
                          SubscriptionSerializer, TagSerializer)
from .shopping_cart import ShoppingList
from recipes.filters import IngredientFilter, RecipeFilter
from recipes.paginators import CustomPaginationClass
from recipes.permissions import RecipesPermission
from users.models import User


class ListRetrieveViewSet(GenericViewSet, mixins.RetrieveModelMixin,
                          mixins.ListModelMixin):
    pass


class ListRetriveCreateUpdateDestroyViewSet(GenericViewSet,
                                            mixins.ListModelMixin,
                                            mixins.RetrieveModelMixin,
                                            mixins.CreateModelMixin,
                                            mixins.UpdateModelMixin,
                                            mixins.DestroyModelMixin):
    pass


class ListViewSet(GenericViewSet, mixins.ListModelMixin):
    pass


class BaseSubscribeViewSet(GenericViewSet, mixins.CreateModelMixin):
    """
    ## ViewSet для подписок / отписок.

    Доступные методы: `POST`, `DELETE`. \n
    Модель подписки состоит из двух связанных полей: `user` и `subscription`,
    где `subscription` обозначает модель на которую идет подписка. \n

    ### Настройка

    Нужно определить ключ аргумента передаваемый с запросом. Для этого
    переопределите переменную `lookup_id_find`. Пример: `recipe_id`.

    Также для создания экземпляра модели нуждно переопределить переменную
    `instanse`.

    Для создания / удаления записи в БД нужно переопределить функции
    `perform_subscribe()` и `perform_unsubscribe()` соответственно.

    Для валидации подписки переопределите фунцкию `comparator_expression()`

    """
    lookup_id_find: str = ...
    instance = ...

    def comparator_expression(self, user, subscription) -> bool:
        ...

    def check_subscription(self, flag, user, subscription):
        if self.comparator_expression(user, subscription) is flag:
            if flag is True:
                raise ParseError('You are already subscribed')
            if flag is False:
                raise ParseError('You aren`t subscribed')

    def perform_subscribe(self, user, subscription):
        ...

    def create(self, request, *args, **kwargs):
        subscription = get_object_or_404(
            self.instance, id=kwargs.get(self.lookup_id_find)
        )
        user = request.user
        serializer = self.get_serializer(subscription)
        self.check_subscription(True, user, subscription)
        self.perform_subscribe(user, subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_unsubscribe(self, user, subscription):
        ...

    def delete(self, request, *args, **kwargs):
        subscription = get_object_or_404(
            self.instance, id=kwargs.get(self.lookup_id_find)
        )
        user = request.user
        self.check_subscription(False, user, subscription)
        self.perform_unsubscribe(user, subscription)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ListRetrieveViewSet):
    permission_classes = []
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(ListRetrieveViewSet):
    permission_classes = []
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    pagination_class = None
    filter_backends = (IngredientFilter, )
    search_fields = ['^name']


class RecipeViewSet(ListRetriveCreateUpdateDestroyViewSet):
    permission_classes = [RecipesPermission]
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginationClass
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class IngredientRecipeViewSet(ListRetrieveViewSet):
    permission_classes = [RecipesPermission]
    serializer_class = IngredientRecipeSerializer
    queryset = Ingredient.objects.all()


class SubscriptionViewSet(ListViewSet):
    permission_classes = [RecipesPermission]
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPaginationClass

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(following__user=user)


class RecipeFavoriteViewSet(BaseSubscribeViewSet):
    permission_classes = [RecipesPermission]
    serializer_class = ResipeFavoriteSerializer
    lookup_id_find = 'recipe_id'
    instance = Recipe

    def comparator_expression(self, user, subscription):
        return user.favoriterecipes.filter(recipe=subscription).exists()

    def perform_subscribe(self, user, subscription):
        user.favoriterecipes.create(recipe=subscription)

    def perform_unsubscribe(self, user, subscription):
        subscribe = user.favoriterecipes.filter(recipe=subscription)
        subscribe.delete()


class SubcribeToUserViewSet(BaseSubscribeViewSet):
    permission_classes = [RecipesPermission]
    serializer_class = SubscriptionSerializer
    lookup_id_find = 'user_id'
    instance = User

    def comparator_expression(self, user, subscription):
        return user.follower.filter(author=subscription).exists()

    def perform_subscribe(self, user, subscription):
        user.follower.create(author=subscription)

    def perform_unsubscribe(self, user, subscription):
        subscribe = user.follower.filter(author=subscription)
        subscribe.delete()


class ShoppingCartViewSet(BaseSubscribeViewSet):
    permission_classes = [RecipesPermission]
    serializer_class = ResipeFavoriteSerializer
    lookup_id_find = 'recipe_id'
    instance = Recipe

    def comparator_expression(self, user, subscription):
        return user.carts.filter(recipe=subscription).exists()

    def perform_subscribe(self, user, subscription):
        user.carts.create(recipe=subscription)

    def perform_unsubscribe(self, user, subscription):
        subscribe = user.carts.filter(recipe=subscription)
        subscribe.delete()


class DownloadShoppingCart(APIView):
    permission_classes = [RecipesPermission]

    def get(self, request):
        user = request.user
        cart = ShoppingList(user)
        list = cart.get_list()
        with open('', 'w') as file:
            file.write(list)
            return FileResponse(
                file, as_attachment=True, filename='список.txt'
            )
