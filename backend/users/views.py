from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from djoser import utils

from .serializers import UserSerializer, RegistrationSerializer, LoginSerializer
from .models import User


class CreateListRetrieveViewSet(GenericViewSet, mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                mixins.CreateModelMixin):
    pass


class UserViewSet(CreateListRetrieveViewSet):
    # Установить пермишены: list, create allallow
    # Установить пермишены: retrieve isAuth
    permission_classes = []
    serializer_class = UserSerializer
    queryset = User.objects.all()

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
    def post(self, request):
        utils.logout_user(request)
        return Response(status.HTTP_204_NO_CONTENT)
