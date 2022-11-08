from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import AuthViewSet, SetPassViewSet, UserViewSet

router_v1 = DefaultRouter()
router_v1.register(r'set_password', SetPassViewSet, basename='set_pass')
router_v1.register(r'', UserViewSet, basename='users')
router_v1.register(r'token/login', AuthViewSet, basename='login')

urlpatterns = [
    path('', include(router_v1.urls))
]
