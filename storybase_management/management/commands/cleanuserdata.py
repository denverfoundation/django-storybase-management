import os
from optparse import make_option
from name_generator import parse_data, generate_names
from name_generator.wc import WeightedChoice
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Remove sensitive user data'
    option_list = BaseCommand.option_list + (
        make_option('--skip-admins',
            action='store_true',
            dest='skip_admins',
            default=True,
            help='Skip admin users when wiping data',
        ),
        make_option('--name-data-dir',
            action='store',
            type='string',
            dest='name_data_dir',
            default=os.path.join(os.getcwd(), 'data'),
            help='Directory containing name database files, downloaded from https://www.census.gov/genealogy/www/data/1990surnames/names_files.html',
        ),
        make_option('--noinput',
            action='store_false', dest='interactive', default=True,
            help="Do NOT prompt the user for input of any kind."),
    )

    def handle(self, *args, **options):
        from storybase_user.utils import is_admin
       
        interactive = options.get('interactive')

        if interactive:
            confirm = raw_input("""You have requested to anonymize all user data. 
This action CANNOT BE REVERSED.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel """)
        else:
            confirm = 'yes'

        if confirm == 'yes':
            file_path = lambda x: os.path.join(options['name_data_dir'], x)
            first_data = parse_data(file_path('dist.female.first')) + parse_data(file_path('dist.male.first'))
            last_data = parse_data(file_path('dist.all.last'))
            first_wc = WeightedChoice(first_data)
            last_wc = WeightedChoice(last_data)

            users = User.objects.all()
            names = generate_names(first_wc, last_wc, users.count(), True)

            for i, user in enumerate(users):
                if options['skip_admins'] and is_admin(user):
                    # Skip admin user
                    self.stderr.write("Skipping admin user %s\n" % (user.username))
                    continue

                (fname, lname) = [n.title() for n in names[i].split(' ')]
                username = "%s.%s" % (fname.lower(), lname.lower())
                email = "%s.%s@floodlightproject.com" % (fname.lower(), lname.lower())
                password = User.objects.make_random_password()

                user.username = username
                user.first_name = fname
                user.last_name = lname
                user.set_password(password)
                user.email = email
                user.save()
        else:
            self.stderr.write("User anonymization cancelled\n")
