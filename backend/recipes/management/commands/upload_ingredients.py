import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient

DATA_DIR = '../data/ingredients.csv'


class Command(BaseCommand):
    """Management комманда для загрузки данных в БД."""
    help = 'Upload ingredients to database'

    def batch(self, bulk: list):
        Ingredient.objects.bulk_create(bulk)

    def handle(self, *args, **options):
        """
        Для загрузки большого объема используется
        `model.objects.bulk_create`.
        """
        try:
            with open(DATA_DIR, 'r', encoding='utf-8') as csvfile:
                ingredients = csv.reader(csvfile, dialect='excel')
                bulk = []
                for count, ingredient in enumerate(ingredients, start=1):
                    data = {
                        'name': ingredient[0],
                        'measurement_unit': ingredient[1]
                    }
                    bulk.append(
                        Ingredient(**data)
                    )
                    if count % 1000 == 0:
                        self.batch(bulk)
                        bulk = []
                self.batch(bulk)
        except Exception as error:
            raise CommandError(error)
        message = f'{count} elements was uploaded to database'
        self.stdout.write(self.style.SUCCESS(message))
        message = f'Total records: {Ingredient.objects.count()}'
        self.stdout.write(message)
