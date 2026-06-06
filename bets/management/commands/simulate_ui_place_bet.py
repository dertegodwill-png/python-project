import os
import random
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.test import Client
from bets.models import Outcome, Bet


def read_password_from_file(username, path='demo_creds.txt'):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(':', 1)
            if len(parts) == 2 and parts[0] == username:
                return parts[1]
    return None


class Command(BaseCommand):
    help = 'Simulate UI login and place a bet for a demo user using the test client'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Demo username to login as')
        parser.add_argument('--outcome-id', type=int, default=None, help='Outcome id to bet on (random if omitted)')
        parser.add_argument('--stake', type=float, default=5.0, help='Stake amount to place')
        parser.add_argument('--password', type=str, default=None, help='Password to use for login (overrides creds file)')
        parser.add_argument('--creds-file', type=str, default='demo_creds.txt', help='Credentials file to read passwords from')

    def handle(self, *args, **options):
        username = options['username']
        outcome_id = options['outcome_id']
        stake = options['stake']

        password = options.get('password') or read_password_from_file(username, path=options.get('creds_file'))
        if password is None:
            self.stdout.write(self.style.WARNING(f'Password not provided and not found in {options.get("creds_file")}; ensure file exists or pass --password'))
            return

        # pick an outcome if none provided
        if outcome_id is None:
            outcome = Outcome.objects.order_by('?').first()
            if not outcome:
                self.stdout.write(self.style.WARNING('No outcomes available. Run generate_matches first.'))
                return
        else:
            try:
                outcome = Outcome.objects.get(pk=outcome_id)
            except Outcome.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Outcome id {outcome_id} not found'))
                return

        client = Client()
        # ensure host header matches allowed hosts; prefer 127.0.0.1 to avoid testserver disallowed host errors
        logged_in = client.login(username=username, password=password)
        self.stdout.write(f'Login for {username}: {"SUCCESS" if logged_in else "FAIL"}')
        if not logged_in:
            return

        # perform POST to place bet view
        url = reverse('bets:place_bet', args=[outcome.pk])
        # Test client uses 'testserver' as host which may be disallowed; set HTTP_HOST header explicitly
        # Try posting with a sensible host; if ALLOWED_HOSTS prevents this, fall back to 'testserver'
        response = client.post(url, {'stake': stake}, follow=True, HTTP_HOST='127.0.0.1')
        if response.status_code == 400 and b'DisallowedHost' in getattr(response, 'content', b''):
            response = client.post(url, {'stake': stake}, follow=True, HTTP_HOST='testserver')
        if response.status_code in (200, 302):
            # check that a bet was created for this user and outcome
            bet_exists = Bet.objects.filter(owner__username=username, outcome=outcome, stake=stake).exists()
            if bet_exists:
                self.stdout.write(self.style.SUCCESS(f'Placed bet for {username} on outcome {outcome} with stake {stake}'))
            else:
                self.stdout.write(self.style.WARNING('POST succeeded but bet record not found — view may not have created the bet'))
        else:
            self.stdout.write(self.style.ERROR(f'POST failed with status {response.status_code}'))
