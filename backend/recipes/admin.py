from django.contrib import admin

from .models import FavoriteRecipe, Ingredient, Recipe, Tag, ShoppingCart


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    search_fields = ('name', 'clug', 'color')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', )
    list_filter = ('measurement_unit', )


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time', 'create')
    search_fields = ('author', 'name', 'create')
    list_filter = ('create', 'cooking_time')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipe)
