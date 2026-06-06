from django.contrib import admin
from .models import Match, Outcome, Bet


class OutcomeInline(admin.TabularInline):
    model = Outcome
    extra = 1


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'finished')
    list_filter = ('finished', 'start_time')
    search_fields = ('title',)
    inlines = [OutcomeInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'start_time', 'finished')
        }),
    )


@admin.register(Outcome)
class OutcomeAdmin(admin.ModelAdmin):
    list_display = ('match', 'name', 'odds', 'is_winner')
    list_filter = ('is_winner', 'match')
    actions = ['mark_as_winner']

    def mark_as_winner(self, request, queryset):
        # Admin should select exactly one outcome to mark as winner per match
        for outcome in queryset:
            # clear previous winners for this match
            Outcome.objects.filter(match=outcome.match, is_winner=True).update(is_winner=False)
            outcome.is_winner = True
            outcome.save()
        self.message_user(request, 'Marked selected outcomes as winner and settled bets.')

    mark_as_winner.short_description = 'Mark selected outcome(s) as winner'


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('owner', 'outcome', 'stake', 'odds_at_place', 'placed_at', 'settled', 'won')
    list_filter = ('settled', 'won')
    actions = []

