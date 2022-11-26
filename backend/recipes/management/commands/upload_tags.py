import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Tag

DATA_DIR = '../data/tags.csv'


class Command(BaseCommand):
    """Management комманда для загрузки данных в БД."""
    help = 'Upload tags to database'

    def handle(self, *args, **options):
        """
        Для загрузки большого объема используется
        `model.objects.bulk_create`.
        """
        try:
            with open(DATA_DIR, 'r', encoding='utf-8') as csvfile:
                ingredients = csv.reader(csvfile, dialect='excel')
                bulk = []
                count = 0
                for name, color, slug in ingredients:
                    bulk.append(
                        Tag(
                            name=name, color=color, slug=slug
                        )
                    )
                    count += 1
                Tag.objects.bulk_create(bulk)
        except Exception as error:
            raise CommandError(error)
        message = f'{count} elements was uploaded to database'
        self.stdout.write(self.style.SUCCESS(message))
        message = f'Total records: {Tag.objects.count()}'
        self.stdout.write(message)
