from optparse import make_option
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Find owner of storybnase models."
    option_list = BaseCommand.option_list + (
        make_option('--type',
            action='store',
            type='string',
            dest='model_type',
            default='story',
            help='Type of model. Can be "story", "section" or "asset".  Default is "story".',
        ),
    )

    def handle(self, *args, **options):
        from storybase_story.models import Section, Story
        from storybase_asset.models import Asset

        model_type = options.get('model_type')

        if model_type == "story":
            qs = Story.objects.all()
            id_attr = 'story_id'
        elif model_type == "section":
            qs = Section.objects.all()
            id_attr ='section_id'
        elif model_type == "asset":
            qs = Asset.objects.all()
            id_attr = 'asset_id'
        else:
            raise CommandError('The type option must be "story", "section" or "asset"')

        try:
            id_value = args[0] 
            filter_kwargs = {
                id_attr: id_value, 
            }
        except IndexError:
            raise CommandError("You must specify a model ID.")

        try:
            model = qs.filter(**filter_kwargs)[0]
        except IndexError:
            raise CommandError("%s with %s %s does not exist." % (model_type,
                id_attr, id_value))

        if model_type == "story":
            user = model.author
        elif model_type == "section":
            user = model.story.author
        elif model_type == "asset":
            user = model.owner

        self.stdout.write("%s with id %s is owned by %s\n" %
            (model_type, id_value, user))
