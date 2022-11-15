from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.validators import UniqueValidator

from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
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

class 
