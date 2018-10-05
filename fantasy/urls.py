from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path('mock/', views.mock, name="mock"),
    path('podcasts/', views.podcasts, name='podcasts'),
    path('research/', views.research, name='research'),
    path('draft/', views.draft, name='draft'),
    path('update_fieldset/', views.update_fieldset, name='update_fieldset'),
    path('drafted_player/', views.drafted_player, name='drafted_player'),
    path('auto/', views.auto, name='auto'),
    path('leaguedraft<leagueid>/', views.leaguedraft, name='leaguedraft'),
    path('leaguehome<leagueid>/', views.leaguehome, name='leaguehome'),
    path('leaguerosters<leagueid>/', views.leaguerosters, name='leaguerosters'),
    path('leaguelineup<leagueid>/', views.leaguelineup, name='leaguelineup'),
    path('swap/', views.swap, name='swap'),
    path('leaguecalendar<leagueid>/', views.leaguecalendar, name='leaguecalendar'),
    path('leaguetransactions<leagueid>/', views.leaguetransactions, name='leaguetransactions'),
    path('leagueplayers<leagueid>/', views.leagueplayers, name='leagueplayers'),
    path('change/', views.change, name='change'),
    path('keep_current/', views.keep_current, name='keep_current'),
    path('update_drafted_players/', views.update_drafted_players, name='update_drafted_players'),
    path('<page>/', views.index),
    path('', views.index, name="index"),
    path('new_league_user', views.new_league_user, name="new_league_user"),
    path('leagues', views.leagues, name="leagues")
]
