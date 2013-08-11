import csv
import json
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from storybase_help.models import Help, HelpTranslation

class Command(BaseCommand):
    args = '<fixture-filename> <csv_file>'
    help = 'Given translation IDs, get the corresponding model IDs'
    option_list = BaseCommand.option_list + (
        make_option('--tid-col-name',
            action='store',
            type='string',
            dest='translation_id_col_name',
            default='translation_id_es',
            help="Name of column containing the translation ID name",
        ),
        make_option('--model-id-col-name',
            action='store',
            type='string',
            dest='model_id_col_name',
            default="help_id",
            help="Name of column containing the model ID name",
        ),
    )

    def handle(self, *args, **options):
        try:
            fixture_filename = args[0]
            csv_filename = args[1]
        except IndexError:
            raise CommandError("You must specify both the filename of the fixture file and CSV file")

        translation_id_col_name = options.get('translation_id_col_name')
        model_id_col_name = options.get('model_id_col_name')

        with open(fixture_filename, "r") as fixture_file:
            with open(csv_filename, "r") as csv_file:
                model_ids = {}
                models = json.load(fixture_file)
                reader = csv.DictReader(csv_file)
                objects = []
                for row in reader:
                    model_ids[row[translation_id_col_name]] = row[model_id_col_name]
                for model in models:
                    if model['model'] == 'storybase_help.helptranslation':
                        fields = model['fields']
                        translation_id = fields['translation_id']
                        help_obj = Help.objects.get(help_id=model_ids[translation_id])
                        fields['help'] = help_obj
                        translation_obj = HelpTranslation(**fields)
                        objects.append(translation_obj)
                for model in objects:
                    model.save()
