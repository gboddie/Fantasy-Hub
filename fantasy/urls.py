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
    path("<page>/", views.index),
    path("", views.index, name="index"),
    path("new_league_user", views.new_league_user, name="new_league_user"),
    path("leagues", views.leagues, name="leagues")
]
