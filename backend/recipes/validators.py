from django.core.exceptions import ValidationError


def validate_min_value(value):
    if value < 1:
        raise ValidationError('Cooking time can`t be less than `1`')
