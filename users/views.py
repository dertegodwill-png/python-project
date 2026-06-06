from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import login


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            # auto-login the new user
            login(request, user)
            messages.success(request, f'Welcome {username}! You are now logged in.')
            return redirect('bets:matches')
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})
