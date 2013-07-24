import csv
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from cms.api import add_plugin
from cms.models import Page, Placeholder
from cms.plugins.text.cms_plugins import TextPlugin

from cmsplugin_storybase.cms_plugins import HelpPlugin
from storybase_help.models import Help

class Command(BaseCommand):
    help = 'Add help imported help items to a CMS page'
    option_list = BaseCommand.option_list + (
        make_option('--language',
            action='store',
            type='string',
            dest='language',
            default='en',
            help="Language code for translation objects",
        ),
        make_option('-p', '--page',
            action='store',
            type='string',
            dest='page_slug',
            default='help',
            help='Slug of page that help items will be added to',
        ),
        make_option('--placeholder',
            action='store',
            type='string',
            dest='placeholder_slot',
            default='twocol-content',
            help='Slot of placeholder that help items will be added to',
        ),
        make_option('--noinput',
            action='store_false', dest='interactive', default=True,
            help="Do NOT prompt the user for input of any kind."),
    )

    def handle(self, *args, **options):
        last_section_title = None
        page_slug = options.get('page_slug')
        placeholder_slot = options.get('placeholder_slot')
        language = options.get('language')
        interactive = options.get('interactive')

        try:
            csv_filename = args[0]
        except IndexError:
            raise CommandError("You must specify a csv filename")

        page = Page.objects.get(title_set__slug=page_slug)
        placeholder = Placeholder.objects.get(page=page, slot=placeholder_slot)

        if interactive:
            confirm = raw_input("""You have requested to replace the help page content 
This action CANNOT BE REVERSED.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel """)
        else:
            confirm = 'yes'

        if confirm != 'yes':
            return

        # Delete existing plugins
        placeholder.get_plugins().delete()

        with open(csv_filename, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                section_title = row[0]
                help_id = row[1]

                # Only proceed for non-header rows  
                if section_title != 'section_title':
                    if last_section_title != section_title:
                        last_section_title = section_title
                        section_title_html = '<h2 class="faq-section">%s</h2>' % section_title
                        add_plugin(placeholder, TextPlugin, language, body=section_title_html)
                    help_item = Help.objects.get(help_id=help_id)
                    add_plugin(placeholder, HelpPlugin, language, help=help_item)
