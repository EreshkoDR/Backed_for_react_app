import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Tag

DATA_DIR = 'data/tags.csv'


class Command(BaseCommand):
    """Management комманда для загрузки данных в БД."""
    help = 'Upload tags to database'

    def batch(self, bulk: list):
        Tag.objects.bulk_create(bulk)

    def handle(self, *args, **options):
        """
        Для загрузки большого объема используется
        `model.objects.bulk_create`.
        """
        try:
            with open(DATA_DIR, 'r', encoding='utf-8') as csvfile:
                tags = csv.reader(csvfile, dialect='excel')
                bulk = []
                for count, tags in enumerate(tags, start=1):
                    data = {
                        'name': tags[0],
                        'color': tags[1],
                        'slug': tags[2],
                    }
                    bulk.append(Tag(**data))
                    if count % 1000 == 0:
                        self.batch(bulk)
                        bulk = []
                self.batch(bulk)
        except Exception as error:
            raise CommandError(error)
        message = f'{count} elements was uploaded to database'
        self.stdout.write(self.style.SUCCESS(message))
        message = f'Total records: {Tag.objects.count()}'
        self.stdout.write(message)
