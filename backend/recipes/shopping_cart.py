from django.db.models import Sum

from .models import Ingredient


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

    def get_txt_file(self):
        text = 'Ваш список покупок:\n\n'
        shopping_list = self.get_shopping_list()
        for recipe in shopping_list:
            name = recipe.get('name')
            unit = recipe.get('measurement_unit')
            amount = recipe.get('amount')
            text += (f'• {name} ({unit}) - {amount}\n')
        return text
