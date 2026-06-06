from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Match, Outcome, Bet
from .forms import BetForm
from django.db.models import Sum


def matches_list(request):
    matches = Match.objects.filter(finished=False).order_by('start_time')
    return render(request, 'bets/matches_list.html', {'matches': matches})


def match_detail(request, pk):
    match = get_object_or_404(Match, pk=pk)
    outcomes = match.outcomes.all()
    return render(request, 'bets/match_detail.html', {'match': match, 'outcomes': outcomes})


@login_required
def place_bet(request, outcome_id):
    outcome = get_object_or_404(Outcome, pk=outcome_id)
    if outcome.match.finished:
        messages.error(request, 'Betting closed for this match.')
        return redirect('bets:matches')

    if request.method == 'POST':
        form = BetForm(request.POST)
        if form.is_valid():
            bet = form.save(commit=False)
            bet.owner = request.user
            bet.outcome = outcome
            bet.save()
            messages.success(request, 'Bet placed successfully!')
            return redirect('bets:dashboard')
    else:
        form = BetForm()
    return render(request, 'bets/place_bet.html', {'form': form, 'outcome': outcome})


@login_required
def dashboard(request):
    bets = Bet.objects.filter(owner=request.user).order_by('-placed_at')
    return render(request, 'bets/dashboard.html', {'bets': bets})


@login_required
def analytics(request):
    bets = Bet.objects.filter(owner=request.user)
    total_bets = bets.count()
    won_bets = bets.filter(won=True)
    lost_bets = bets.filter(won=False)

    total_staked = bets.aggregate(Sum('stake'))['stake__sum'] or 0
    total_won_amount = sum((b.potential_return() or 0) for b in won_bets)
    net_profit = total_won_amount - total_staked

    win_rate = (won_bets.count() / total_bets * 100) if total_bets > 0 else 0

    context = {
        'total_bets': total_bets,
        'total_staked': total_staked,
        'net_profit': net_profit,
        'win_rate': round(win_rate, 2),
    }
    return render(request, 'bets/analytics.html', context)
