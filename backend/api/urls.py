from django.urls import include, path
from rest_framework import routers

from users.views import SetPasswordView, UserViewSet
from recipes.views import (DownloadShoppingCart, IngredientViewSet,
                           RecipeFavoriteViewSet, RecipeViewSet,
                           ShoppingCartViewSet, SubcribeToUserViewSet,
                           SubscriptionViewSet, TagViewSet)

router_v1 = routers.DefaultRouter()
router_v1.register(
    r'users/subscriptions', SubscriptionViewSet, basename='subs'
)
router_v1.register(r'users', UserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubcribeToUserViewSet,
    basename='subscribes'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shopping_cart'
)
router_v1.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    RecipeFavoriteViewSet,
    basename='favorites'
)

urlpatterns = [
    path('recipes/download_shopping_cart/', DownloadShoppingCart.as_view()),
    path('users/set_password/', SetPasswordView.as_view()),
    path('', include(router_v1.urls)),
    path('auth/', include('users.urls')),
]
