from django.db.models import Sum

from .models import Ingredient
from backend.settings import BASE_DIR


class ShoppingList:
    def __init__(self, user):
        self.user = user

    def get_shopping_list(self):
        arr = (
            Ingredient.objects
            .prefetch_related('ingredientrecipes')
            .filter(ingredientrecipes__recipes__carts__user=self.user)
            .values('name', 'measurement_unit')
            .annotate(amount=Sum('ingredientrecipes__amount'))
            .order_by('name')
        )
        return arr

    def create_text(self) -> str:
        text = 'Ваш список покупок:\n\n'
        shopping_list = self.get_shopping_list()
        for recipe in shopping_list:
            name = recipe.get('name')
            unit = recipe.get('measurement_unit')
            amount = recipe.get('amount')
            text += (f'• {name} ({unit}) - {amount}\n')
        return text

    def get_file_direction(self):
        direction = BASE_DIR / f'media/shopping_list/{self.user.username}.txt'
        with open(direction, 'w') as file:
            file.write(self.create_text())
        return direction
