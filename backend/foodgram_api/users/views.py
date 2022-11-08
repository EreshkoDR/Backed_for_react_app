from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from .models import User
from .serializers import (AuthSerializer, RegistrationUserSerializer,
                          SetPassSerializer, UserSerializer)


class CreateListRetrieveModelViewSet(
                                     GenericViewSet, mixins.CreateModelMixin,
                                     mixins.ListModelMixin,
                                     mixins.RetrieveModelMixin):
    """Миксин `Create`, `List`, `Retrieve`."""
    pass


class CreateModelViewSet(GenericViewSet, mixins.CreateModelMixin):
    pass


class AuthViewSet(CreateModelViewSet):
    """Вьюсет аутентификации по логину и паролю."""
    queryset = User.objects.all()
    serializer_class = AuthSerializer
    permission_classes = []
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data.get('auth_token')
        return Response({'auth_token': token}, status=status.HTTP_201_CREATED)


class SetPassViewSet(CreateModelViewSet):
    """Вьюсет создания нового пароля."""
    queryset = User.objects.all()
    serializer_class = SetPassSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        # Создать валидатор для проверки правильности
        serializer.is_valid(raise_exception=True)
        current_pass = serializer.validated_data.get('current_password')
        new_pass = serializer.validated_data.get('new_password')
        user: User = request.user
        if user.password != current_pass:
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        user.password = new_pass
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(CreateListRetrieveModelViewSet):
    """
    ## Вьюсет пользователей.
    GET-request `/users/` возвращает список пользователей.\n
    GET-request `/users/me/` возвращает данные об авторизированном
    пользователе.\n
    POST-request `/users/` создает нового пользователя.\n
    """
    queryset = User.objects.all()
    permission_classes = []
    # authentication_classes = []

    def get_serializer_class(self):
        if self.action == 'create':
            return RegistrationUserSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        first_name = serializer.validated_data.get('first_name')
        last_name = serializer.validated_data.get('last_name')
        password = serializer.validated_data.get('password')
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        response = {
            'email': user.email,
            'id': user.pk,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        return Response(response, status=status.HTTP_201_CREATED)

    def get_object(self):
        """
        Отлавливаем эндпоинт `users/me/`
        и возвращаем данные авторизированного пользователя.
        """
        if self.kwargs.get('pk') == 'me':
            obj = self.request.user
            return obj
        return super().get_object()
