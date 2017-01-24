from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.utils import formats
import pprint

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('command')
        parser.add_argument('userid',
                            nargs='?'
                        )

    def handle(self, *args, **options):
        print "IV users"

        command = options['command'].lower()

        if command == 'list':
            self.list_users()
        elif command == 'active':
            self.toggle_active(int(options['userid']))
        elif command == 'staff':
            self.toggle_staff(int(options['userid']))

    def toggle_active(self, userid):
        user = User.objects.get(pk=userid)
        user.is_active = not user.is_active
        user.save()

        print "User is now {}".format('active' if user.is_active else 'inactive')

        self.print_user_header()
        self.print_user(user)

    def toggle_staff(self, userid):
        user = User.objects.get(pk=userid)
        user.is_staff = not user.is_staff
        user.save()

        print "User is now {}".format('staff' if user.is_staff else 'not staff')

        self.print_user_header()
        self.print_user(user)

    def list_users(self):
        self.print_user_header()

        for user in User.objects.all():
            self.print_user(user)

    def print_user_header(self):
        print "{:<3} {:<24} {:<15} {:<15} {:<15} {:<30} {:<21} {:<21} {:<8} {:<9}".format('uid',
                                                                                    'username',
                                                                                    'provider',
                                                                                    'first',
                                                                                    'last',
                                                                                    'email',
                                                                                    'last_login',
                                                                                    'date_joined',
                                                                                    'is staff',
                                                                                    'is active')

    def print_user(self, user):
            print "{:<3} {:<24} {:<15} {:<15} {:<15} {:<30} {:<21} {:<21} {:<8} {:<9}".format(user.id, 
                                                                                         user.username,
                                                                                         user.social_auth.get().provider,  
                                                                                         user.first_name,
                                                                                         user.last_name,
                                                                                         user.email,
                                                                                         formats.date_format(user.last_login, "SHORT_DATETIME_FORMAT"),
                                                                                         formats.date_format(user.date_joined, "SHORT_DATETIME_FORMAT"),
                                                                                         user.is_staff,
                                                                                         user.is_active)
#            print user.social_auth.get().provider
