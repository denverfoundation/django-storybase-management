from django.core.management.base import BaseCommand
from django.utils.html import strip_tags

class Command(BaseCommand):
    help = 'Get a report about the lengths of different aspects of stories in the system'
    option_list = BaseCommand.option_list

    def get_story_info(self):
        """
        Get information about the length of content for stories
        """
        from storybase_story.models import Story
        # I thought of trying to do this at the database level, i.e. using
        # StoryTranslation.objects.extra(), but we need to strip html from
        # the sumary field
        total_title_length = 0
        total_summary_length = 0
        queryset = Story.objects.published()
        num_objects = queryset.count()
        for story in queryset:
            total_title_length += len(story.title)
            total_summary_length += len(strip_tags(story.summary))
        return (total_title_length / num_objects, total_summary_length / num_objects) 

    def handle(self, *args, **options):
        avg_story_title_length, avg_story_summary_length = self.get_story_info()
        self.stdout.write("Story\n")
        self.stdout.write("-----\n\n")
        self.stdout.write("Average title length: %d\n" % avg_story_title_length)
        self.stdout.write("Average summary length: %d\n" % avg_story_summary_length)
