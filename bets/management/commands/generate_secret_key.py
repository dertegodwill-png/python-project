import secrets
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate a strong Django SECRET_KEY for use in production .env'

    def handle(self, *args, **options):
        key = secrets.token_urlsafe(50)
        self.stdout.write('Add this to your .env as SECRET_KEY:')
        self.stdout.write(key)