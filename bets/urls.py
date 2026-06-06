from django.urls import path
from . import views

app_name = 'bets'

urlpatterns = [
    path('', views.matches_list, name='matches'),
    path('match/<int:pk>/', views.match_detail, name='match_detail'),
    path('outcome/<int:outcome_id>/place/', views.place_bet, name='place_bet'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
]
