from django.core.management.base import BaseCommand

from storybase_management.utils import model_stats

def caption_length(asset):
    return len(asset.caption)

def asset_story_id(asset):
    if not asset.stories.count():
        return None
    
    return asset.stories.all()[0].story_id

class Command(BaseCommand):
    help = 'Get the min/max and average lengths of captions for image assets'

    def handle(self, *args, **options):
        from storybase_asset.models import Asset
        from storybase_story.models import Story
        images = Asset.objects.filter(type='image', status='published').select_subclasses()
        (min_val, max_val, avg_val) = model_stats(images, caption_length, 'asset_id', asset_story_id) 

        for (label, val) in zip(["Min", "Max", "Avg"], [min_val, max_val, avg_val]):
            asset = Asset.objects.filter(asset_id=val['asset_id']).select_subclasses()[0]
            story = Story.objects.get(story_id=val['story_id'])
            self.stdout.write("%s: %d ('%s') in story %s\n" %
                (label, val['value'], asset.caption, story.get_absolute_url()))
