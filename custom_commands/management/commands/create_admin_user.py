import os
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Creates Admin User'

    def handle(self, *args, **options):
        try:
            username = os.getenv("ADMIN_USERNAME", "admin")
            email = os.getenv("ADMIN_EMAIL", "admin@gmail.com")
            password = os.getenv("ADMIN_PASSWORD", "admin")

            if settings.ENV_NAME != "production" and \
                    (not User.objects.filter(username=username).exists()):
                User.objects.create_superuser(username, email, password)
        except Exception as e:
            raise CommandError(e)

        self.stdout.write(self.style.SUCCESS('Successfully created user "%s"' % username))
