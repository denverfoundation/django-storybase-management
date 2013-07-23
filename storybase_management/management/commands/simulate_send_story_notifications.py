from datetime import datetime
from optparse import make_option
import time

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = ("Simulate sending story notification emails\n\n"
            "This is implemented as a management command rather than as a\n"
            "test because it's easiest to use the real database and there's\n"
            "not really a condition to test and see if the test passes or\n"
            "fails. It's really just to see how email sending performs under\n"
            "load.")
    option_list = BaseCommand.option_list + (
        make_option('--number',
            action='store',
            type='int',
            dest='number',
            default=10,
            help='Number of notifications to send',
        ),
        make_option('--type',
            action='store',
            type='string',
            dest='notification_type',
            default='published',
            help='Notification type for notifications to be created',
        ),
    )

    def create_notifications(self, notification_type):
        from storybase_messaging.models import StoryNotification
        from storybase_story.models import Story

        stories = Story.objects.filter(status='published')[:self.num_notifications]
        self.notification_pks = []
        for story in stories:
            notification = StoryNotification.objects.create(notification_type='published',
                story=story, send_on=datetime.now())
            self.notification_pks.append(notification.pk)

    def send_notifications(self):
        from storybase_messaging.models import StoryNotification
        t1 = time.time()
        StoryNotification.objects.filter(pk__in=self.notification_pks).emails().send()
        latency = time.time() - t1
        self.stdout.write("%d notifications sent in %f seconds\n" % (self.num_notifications, latency))

    def cleanup_notifications(self):
        from storybase_messaging.models import StoryNotification
        StoryNotification.objects.filter(pk__in=self.notification_pks).delete()
        
    def handle(self, *args, **options):
        self.num_notifications = options.get('number')
        notification_type = options.get('notification_type')
        self.create_notifications(notification_type)
        self.send_notifications()
        self.cleanup_notifications()
