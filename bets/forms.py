from django import forms
from .models import Bet


class BetForm(forms.ModelForm):
    class Meta:
        model = Bet
        fields = ['stake']
        widgets = {
            'stake': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
