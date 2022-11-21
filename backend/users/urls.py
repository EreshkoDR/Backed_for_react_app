from django.urls import path

from .views import LoginView, LogoutView

urlpatterns = [
    path('token/login/', LoginView.as_view(), name='login'),
    path('token/logout/', LogoutView.as_view(), name='logout'),
]