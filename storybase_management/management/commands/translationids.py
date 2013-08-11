import csv
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db.models import get_model

class Command(BaseCommand):
    args = '<csv-filename> <model>'
    help = 'Given translation IDs, get the corresponding model IDs'
    option_list = BaseCommand.option_list + (
        make_option('--column-name',
            action='store',
            type='string',
            dest='column_name',
            default='translation_id',
            help="Name of column containing translation IDs. Default is 'translation_id'",
        ),
    )

    def handle(self, *args, **options):
        try:
            csv_filename = args[0]
            app_model_name = args[1]
        except IndexError:
            raise CommandError("You must specify both the filename of the CSV file with thr translation IDs as well as the model name")

        column_name = options.get('column_name') 
        (app_name, model_name) = app_model_name.split('.', 1 )
        translation_field_name = "%stranslation" % model_name.lower()
        model_class = get_model(app_name, model_name)
        with open(csv_filename, "r") as csv_file:
            reader = csv.DictReader(csv_file)
            writer = csv.DictWriter(self.stdout, fieldnames=['translation_id', 'model_id'])
            writer.writeheader()
            for row in reader:
                translation_id = row[column_name]
                query_kwargs = {
                    translation_field_name + "__translation_id": translation_id, 
                }
                model = model_class.objects.get(**query_kwargs)
                writer.writerow({
                    'translation_id': translation_id,
                    'model_id': getattr(model, model_name.lower() + '_id'),
                })
