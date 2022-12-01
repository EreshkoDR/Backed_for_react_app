import csv

from django.core.management.base import BaseCommand, CommandError

from recipes.models import Tag

DATA_DIR = 'data/tags.csv'


class Command(BaseCommand):
    """Management комманда для загрузки данных в БД."""
    help = 'Upload tags to database'

    def batch(self, bulk: list):
        Tag.objects.bulk_create(bulk)

    def exists_record(self, queryset, name: str) -> bool:
        return queryset.filter(name=name).exists()

    def handle(self, *args, **options):
        """
        Для загрузки большого объема используется
        `model.objects.bulk_create`.
        """
        try:
            with open(DATA_DIR, 'r', encoding='utf-8') as csvfile:
                tags = csv.reader(csvfile, dialect='excel')
                current_ingredients = Tag.objects.all()
                bulk = []
                count = 0
                for tag in tags:
                    data = {
                        'name': tag[0],
                        'color': tag[1],
                        'slug': tag[2],
                    }
                    if not self.exists_record(current_ingredients, tag[0]):
                        bulk.append(Tag(**data))
                        count += 1
                    if len(bulk) % 1000 == 0:
                        self.batch(bulk)
                        bulk = []
                self.batch(bulk)
        except Exception as error:
            raise CommandError(error)
        message = f'{count} elements was uploaded to database'
        self.stdout.write(self.style.SUCCESS(message))
        message = f'Total records: {Tag.objects.count()}'
        self.stdout.write(message)
