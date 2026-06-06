import random
import secrets
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client
from bets.models import Outcome, Bet

User = get_user_model()

NAMES = ['alice', 'bob', 'carol', 'dave']


class Command(BaseCommand):
    help = 'Create demo users and place sample bets for them'

    def add_arguments(self, parser):
        parser.add_argument('--bets', type=int, default=2, help='Number of bets to place per user')
        parser.add_argument('--randomize-passwords', action='store_true', help='Generate random passwords for users (overwrites existing)')
        parser.add_argument('--output-file', type=str, default=None, help='Write generated credentials to this file')
        parser.add_argument('--verify', action='store_true', help='Verify created credentials by attempting to log in (uses Django test client)')

    def handle(self, *args, **options):
        num_bets = options.get('bets', 2)
        randomize = options.get('randomize_passwords', False)
        out_file = options.get('output_file')
        verify = options.get('verify', False)

        outcomes = list(Outcome.objects.all())
        if not outcomes:
            self.stdout.write(self.style.WARNING('No outcomes found. Run generate_matches first.'))
            return

        creds = {}
        created_users = []

        for name in NAMES:
            user, created = User.objects.get_or_create(username=name, defaults={'email': f'{name}@example.com'})
            if created or randomize:
                # generate a secure random password
                pwd = secrets.token_urlsafe(10)
                user.set_password(pwd)
                user.save()
                creds[user.username] = pwd
            else:
                # existing user and not randomizing: leave password unchanged
                creds[user.username] = '(unchanged)'

            created_users.append(user)

            # place num_bets random bets
            for _ in range(num_bets):
                outcome = random.choice(outcomes)
                stake = round(random.uniform(1, 50), 2)
                Bet.objects.create(owner=user, outcome=outcome, stake=stake)

        # Optionally write credentials to a file with restrictive permissions
        if out_file:
            try:
                with open(out_file, 'w', encoding='utf-8') as f:
                    for u, p in creds.items():
                        f.write(f"{u}:{p}\n")
                # try to set restrictive permissions (POSIX); on Windows this may be ignored
                try:
                    os.chmod(out_file, 0o600)
                except Exception:
                    pass
                self.stdout.write(self.style.SUCCESS(f'Wrote credentials to {out_file}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Failed to write credentials file: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Created/ensured {len(created_users)} users and placed {num_bets} sample bets each'))
        for u in created_users:
            self.stdout.write(f'- {u.username} (password: {creds.get(u.username)})')

        # Optionally verify logins using Django test client
        if verify:
            client = Client()
            self.stdout.write('\nVerifying logins:')
            for username, password in creds.items():
                if password == '(unchanged)':
                    self.stdout.write(f'- {username}: skipped (password unchanged)')
                    continue
                logged_in = client.login(username=username, password=password)
                    self.stdout.write(f"- {username}: {'SUCCESS' if logged_in else 'FAIL'}")
