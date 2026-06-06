from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Match(models.Model):
    home_team = models.CharField(max_length=255)
    away_team = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_time', '-created_at']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.title:
            self.title = f"{self.home_team} vs {self.away_team}"
        super().save(*args, **kwargs)
        if is_new:
            Outcome.objects.create(match=self, name=f"{self.home_team} Win", odds=2.00)
            Outcome.objects.create(match=self, name="Draw", odds=3.00)
            Outcome.objects.create(match=self, name=f"{self.away_team} Win", odds=2.00)

    def __str__(self):
        return self.title


class Outcome(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='outcomes')
    name = models.CharField(max_length=200)
    odds = models.DecimalField(max_digits=6, decimal_places=2)
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.match.title} - {self.name} @ {self.odds}"


class Bet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bets')
    outcome = models.ForeignKey(Outcome, on_delete=models.CASCADE, related_name='bets', null=True, blank=True)
    stake = models.DecimalField(max_digits=10, decimal_places=2)
    odds_at_place = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    placed_at = models.DateTimeField(auto_now_add=True)
    settled = models.BooleanField(default=False)
    won = models.BooleanField(null=True)
    payment_validated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # capture odds at time of placing the bet
        if not self.odds_at_place and self.outcome is not None:
            self.odds_at_place = self.outcome.odds
        super().save(*args, **kwargs)

    def potential_return(self):
        if self.odds_at_place is None:
            return None
        return self.stake * self.odds_at_place

    def profit(self):
        if self.won is True:
            return self.potential_return() - self.stake
        if self.won is False:
            return -self.stake
        return None

    def __str__(self):
        return f"{self.owner} -> {self.outcome} ({self.stake}@{self.odds_at_place})"


@receiver(post_save, sender=Outcome)
def settle_bets_on_outcome_save(sender, instance, **kwargs):
    """When an Outcome is marked as winner, settle all bets for that match.

    Admin should mark the winning Outcome.is_winner=True for a match. This handler
    marks the match finished and settles all unsettled bets of the match's outcomes.
    """
    if instance.is_winner:
        match = instance.match
        # mark match finished
        if not match.finished:
            match.finished = True
            match.save(update_fields=['finished'])
        # settle bets for all outcomes of this match
        for outcome in match.outcomes.all():
            is_winning_outcome = (outcome.pk == instance.pk)
            bets = outcome.bets.filter(settled=False)
            for bet in bets:
                bet.settled = True
                bet.won = is_winning_outcome
                bet.save(update_fields=['settled', 'won'])
