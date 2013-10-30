from django.core.management.base import BaseCommand

from storybase_management.utils import model_stats

def title_length(story):
    return len(story.title)

def get_story_id(story):
    return story.story_id

class Command(BaseCommand):
    help = 'Get the min/max and average lengths of titles for stories'

    def handle(self, *args, **options):
        from storybase_story.models import Story
        stories = Story.objects.filter(status='published')
        (min_val, max_val, avg_val) = model_stats(stories, title_length, 
                                                  'story_id', get_story_id)

        for (label, val) in zip(["Min", "Max", "Avg"], [min_val, max_val, avg_val]):
            story = Story.objects.get(story_id=val['story_id'])
            self.stdout.write("%s: %d ('%s') in story %s\n" %
                (label, val['value'], story.title, story.get_absolute_url()))
