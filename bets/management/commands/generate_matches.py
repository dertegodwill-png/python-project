import random
from django.core.management.base import BaseCommand
from django.utils import timezone

from bets.models import Match, Outcome

TEAMS = [
    'Lions', 'Tigers', 'Bears', 'Wolves', 'Eagles', 'Hawks', 'Sharks', 'Dragons', 'Raptors', 'Kings'
]


def random_title():
    a, b = random.sample(TEAMS, 2)
    return f"{a} vs {b}"


class Command(BaseCommand):
    help = 'Generate random matches with outcomes for testing'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10, help='Number of matches to create')

    def handle(self, *args, **options):
        count = options['count']
        created = []
        for _ in range(count):
            title = random_title()
            match = Match.objects.create(title=title, start_time=timezone.now())
            # create 2 or 3 outcomes
            num_outcomes = random.choice([2, 2, 3])
            for i in range(num_outcomes):
                name = f"Outcome {i+1}"
                # generate reasonable odds between 1.2 and 4.0
                odds = round(random.uniform(1.2, 4.0), 2)
                Outcome.objects.create(match=match, name=name, odds=odds)
            created.append(match)

        self.stdout.write(self.style.SUCCESS(f"Created {len(created)} matches"))
        for m in created:
            self.stdout.write(f"- {m.title} ({m.start_time}) with {m.outcomes.count()} outcomes")
