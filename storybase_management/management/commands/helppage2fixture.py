from collections import OrderedDict
from optparse import make_option

import csv
import lxml.html
import requests
import uuid

from django.core import serializers
from django.core.management.base import BaseCommand, CommandError

from storybase.utils import slugify
from storybase_help.models import Help, HelpTranslation

class Command(BaseCommand):
    help = 'Convert help from a Django CMS page into a fixture of Help model instances'
    option_list = BaseCommand.option_list + (
        make_option('--language',
            action='store',
            type='string',
            dest='language',
            default='en',
            help="Language code for translation objects",
        ),
        make_option('--title-selector',
            action='store',
            type='string',
            dest='title_selector',
            default=".//*[contains(concat(' ',normalize-space(@class),' '),' faq-question ')]",
            help="XPATH selector for title elements",
        ),
        make_option('--body-selector',
            action='store',
            type='string',
            dest='body_selector',
            default="*[contains(concat(' ',normalize-space(@class),' '),' faq-answer ')]",
            help="XPATH selector for body elements",
        ),
        make_option('--section-selector',
            action='store',
            type='string',
            dest='section_selector',
            default="*[contains(concat(' ',normalize-space(@class),' '),' faq-section ')]",
            help="XPATH selector for section heading elements",
        ),
        make_option('--sections-csv-file',
            action='store',
            type='string',
            dest='sections_csv_file',
            default="",
            help="Filename to output section to help mapping",
        ),
    )

    def handle(self, *args, **options):
        def get_section_title(el, sel):
            relative_sel = "./preceding-sibling::%s[1]" % sel
            return el.xpath(relative_sel)[0].text_content().strip()

        try:
            url = args[0]
        except IndexError:
            raise CommandError("You must specify a url for the help page")

        title_selector = options.get('title_selector')
        body_selector = options.get('body_selector')
        section_selector = options.get('section_selector')
        language = options.get('language')
        sections_csv_file = options.get('sections_csv_file')

        help_items = []
        sections = OrderedDict()

        r = requests.get(url)

        html = lxml.html.fromstring(r.text)
        titles = html.xpath(title_selector)
        section_els = html.xpath(".//%s" % section_selector)
        for el in section_els:
            title = el.text_content().strip() 
            sections[title] = []

        for el in titles:
            title = el.text_content().strip()
            body_el = el.xpath("./following::%s[1]" % body_selector)[0]
            body = "\n".join([lxml.html.tostring(child) for child in body_el])
            section_title = get_section_title(el, section_selector)
            help_translation = HelpTranslation(title=title, body=body, language=language)
            help_translation.translation_id = str(uuid.uuid4()).replace('-', '')
            help_item = Help(searchable=True,
                help_id=str(uuid.uuid4()).replace('-', ''),
                slug=slugify(title))
            help_items.append(help_item)
            help_translation.help = help_item
            help_items.append(help_translation)
            sections[section_title].append(help_item.help_id)


        data = serializers.serialize('json', help_items, indent=2, use_natural_keys=True)
        self.stdout.write(data)

        if sections_csv_file:
            with open(sections_csv_file, 'wb') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['section_title', 'help_id'])
                for section_title in sections:
                    for help_id in sections[section_title]:
                        csvwriter.writerow([section_title, help_id])
