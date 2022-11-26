from djoser import utils
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, mixins

from backend.paginators import CustomPaginationClass
from backend.permissions import IsUserPermission
from .models import User
from .serializers import (ChangePasswordSerializer, LoginSerializer,
                          RegistrationSerializer, UserSerializer)


class CreateListRetrieveViewSet(GenericViewSet, mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                mixins.CreateModelMixin):
    pass


class UserViewSet(CreateListRetrieveViewSet):
    permission_classes = [IsUserPermission]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = CustomPaginationClass

    def get_permissions(self):
        if self.action in ['list', 'create']:
            return []
        return super().get_permissions()

    def create(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data.pop('password')
        user = User.objects.create(**serializer.validated_data)
        user.set_password(password)
        user.save()
        serializer.instance = user
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_object(self):
        if self.action == 'retrieve':
            return self.request.user
        return super().get_object()


class SetPasswordView(APIView):
    permission_classes = [IsUserPermission]

    def post(self, request):
        user = request.user
        serialzer = ChangePasswordSerializer(user, data=request.data)
        serialzer.is_valid(raise_exception=True)
        new_password = serialzer.validated_data.get('new_password')
        self.request.user.set_password(new_password)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LoginView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data.get('user')
        token = utils.login_user(request, user)
        return Response(
            {'auth_token': str(token)},
            status=status.HTTP_201_CREATED
        )


class LogoutView(APIView):
    permission_classes = [IsUserPermission]

    def post(self, request):
        utils.logout_user(request)
        return Response(status.HTTP_204_NO_CONTENT)
