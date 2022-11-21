from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValueError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate

from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150, write_only=True)

    def validate_username(self, value: str):
        incorrect_names = ['me', 'set_password']
        if value.lower() in incorrect_names:
            raise ValidationError(f'You couldn`t use `{value}` like username')
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValueError as error:
            raise ValidationError(error)
        return value

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name', 'password')


class LoginSerializer(serializers.Serializer):
    password = serializers.CharField()
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError('User with that email doesn`t exist')
        return value

    def validate(self, attrs):
        user = User.objects.get(email=attrs.get('email'))
        password = attrs.get('password')
        if not user.check_password(password):
            raise ValidationError('Incorrect password')
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=150)
    current_password = serializers.CharField(max_length=150)

    def validate_current_password(self, value):
        user: User = self.context['request'].user
        if user.password != value:
            raise ValidationError('Incorrect password')
        return value


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='check_subscribed'
    )

    def check_subscribed(self, author: User):
        """
        Проверка на подписку.
        Если есть подписка на пользователя, поле возвращается с флагом `True`.
        """
        try:
            user: User = self.context['request'].user
            if user.is_authenticated:
                return user.follower.filter(author=author).exist()
            return False
        except Exception:
            return False

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')
