from django.urls import include, path
from rest_framework import routers

from .views import LoginView, LogoutView, SetPasswordView, UserViewSet
from recipes.views import SubcribeToUserViewSet, SubscriptionViewSet

router_v1 = routers.DefaultRouter()
router_v1.register(r'subscriptions', SubscriptionViewSet, basename='subs')
router_v1.register(r'', UserViewSet, basename='users')
router_v1.register(r'(?P<user_id>\d+)/subscribe',
                   SubcribeToUserViewSet,
                   basename='subscribes')

urlpatterns = [
    path('set_password/', SetPasswordView.as_view(), name='set_password'),
    path('', include(router_v1.urls)),
    path('token/login/', LoginView.as_view(), name='login'),
    path('token/logout/', LogoutView.as_view(), name='logout'),
]
