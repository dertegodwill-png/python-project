import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "betting_tracker.settings")
django.setup()

from bets.models import Match, Outcome

def create_test_match():
    m = Match.objects.create(
        home_team="Chelsea",
        away_team="Arsenal",
    )
    print(f"Created Match: {m.title}")
    outcomes = m.outcomes.all()
    print(f"Outcomes created: {[o.name for o in outcomes]}")

if __name__ == "__main__":
    create_test_match()
