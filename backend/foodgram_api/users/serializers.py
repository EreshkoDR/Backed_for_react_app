from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.tokens import AccessToken

from .models import User


class AuthSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    @classmethod
    def get_token(cls, user):
        return AccessToken.for_user(user)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = get_object_or_404(User, email=email, password=password)
        token = self.get_token(user)
        attrs['auth_token'] = str(token)
        return attrs


class RegistrationUserSerializer(serializers.Serializer):
    """Сериализатор регистрации пользователя."""
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(
        max_length=150
    )
    last_name = serializers.CharField(
        max_length=150
    )
    password = serializers.CharField(
        max_length=150
    )

    def validate(self, attrs):
        """Валидатор поля `username`. `username` != `me`."""
        uncorrect_names = ['me', 'set_password']
        username = attrs.get('username')
        try:
            if username.lower() in uncorrect_names:
                msg = (
                    f'Вы не можете использовать "{username}"'
                    'в качестве username'
                )
                raise serializers.ValidationError(msg)
        except AttributeError:
            return attrs
        return attrs


class SetPassSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    current_password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели `User`."""
    class Meta:
        model = User
        fields = (
            'email', 'username', 'id', 'first_name', 'last_name'
        )
