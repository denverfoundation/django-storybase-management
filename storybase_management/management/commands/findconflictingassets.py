from optparse import make_option
import csv
try:
    import texttable
except ImportError:
    texttable = None
from django.core.management.base import BaseCommand
from storybase_story.models import Section, SectionAsset

class Command(BaseCommand):
    help = 'Identify assets assigned to the same section container.  See https://github.com/PitonFoundation/atlas/issues/535'
    option_list = BaseCommand.option_list + (
        make_option('--csv',
            action='store_true',
            dest='output_csv',
            default=False,
            help='Generate output in CSV',
        ),
    )

    cols = [
        'Section ID',
        'Asset ID',
        'Container',
        'Weight',
        'Section Title',
        'Story Title',
        'Story ID',
        'Story Author',
        'Story Status',
    ]

    def add_header(self, csv_writer=None, table=None):
        if csv_writer:
            csv_writer.writerow(self.cols)
        else:
            if table:
                cols_width = [len(header) for header in self.cols]
                table.set_cols_width(cols_width)
                table.header(self.cols)
            else:
                self.stdout.write("%s\n" % (self.cols.join(" | ")))
                
    def add_row(self, sa, csv_writer=None, table=None):
        row = [
            sa.section.section_id,
            sa.asset.asset_id,
            sa.container.name,
            sa.weight,
            sa.section.title,
            sa.section.story.title,
            sa.section.story.story_id,
            sa.section.story.author.username,
            sa.section.story.status,
        ]
        if csv_writer:
            csv_writer.writerow(row)
        else:
            if table:
                table.add_row(row)
            else:
                self.stdout.write("%s\n" % (row.join(" | ")))

    def render(self, csv_writer=None, table=None):
        if table:
            self.stdout.write(table.draw())

        if csv_writer is not None:
            self.stdout.write("\n\n")
         
    def find_conflicts(self):
        """Find all conflicting assets"""
        conflicts = {}

        for section in Section.objects.all():
            seen = {}
            scn_conflicts = []
            for sa in SectionAsset.objects.filter(section=section):
                key = "%s:%s:%d" % (section.section_id, sa.container, sa.weight)
                if key in seen:
                    if len(seen[key]) == 1:
                        # First time we run into a conflict
                        # Make an entry in the conflicts dict
                        scn_conflicts.append(key)
                        # First time we run into conflict, show a message
                        #print "multiple assets found for section %s (%s), container %s and weight %d in story %s (%s)" % (section.title, section.section_id, sa.container, sa.weight, section.story.title, section.story.story_id)
                else:
                    seen[key] = []
                seen[key].append(sa)
            for key in scn_conflicts:
                conflicts[key] = seen[key]

        return conflicts

    def handle(self, *args, **options):
        output_csv = options.get('output_csv')
        csv_writer = None
        table = None
        if output_csv:
            csv_writer = csv.writer(self.stdout)
        else:
            if texttable:
                table = texttable.Texttable()

        self.add_header(csv_writer, table)
        conflicts = self.find_conflicts()
        for key, sas in conflicts.items():
            for sa in sas:
                self.add_row(sa, csv_writer, table)

        self.render(csv_writer, table)
