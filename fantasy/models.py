from django.db import models
from django.contrib.auth.models import User
from django import forms
from datetime import datetime

# 32 NFL teams
class Teams(models.Model):
    location = models.CharField(max_length=15)
    mascot = models.CharField(max_length=10)

    def __str__(self):
        return '%s %s' % (self.location, self.mascot)

# All active players
class Players(models.Model):
    name = models.CharField(max_length=64)
    age = models.IntegerField()
    #offense/defense/specialteams
    phase = models.CharField(max_length=20, null=True)
    position = models.CharField(max_length=3)
    jersey = models.IntegerField()
    team = models.ForeignKey(Teams, blank=True, on_delete=models.CASCADE)
    height = models.CharField(max_length=5)
    weight = models.IntegerField()
    total_draft_positions = models.IntegerField(default=0)
    total_number_drafts = models.IntegerField(default=0)

    def __str__(self):
        return '%s %s' % (self.position, self.name)

# Statistics for each player by week
class Stats(models.Model):
    player = models.ForeignKey(Players, on_delete=models.CASCADE)
    year = models.CharField(max_length=4)
    passing = models.IntegerField(default=0)
    rushing = models.IntegerField(default=0)
    receiving = models.IntegerField(default=0)
    catches = models.IntegerField(default=0)
    kick_return = models.IntegerField(default=0)
    punt_return = models.IntegerField(default=0)
    fumbles = models.IntegerField(default=0)
    Interceptions = models.IntegerField(default=0)
    sacks = models.IntegerField(default=0)
    safetys = models.IntegerField(default=0)
    TDs = models.IntegerField(default=0)

    def __str__(self):
        return '%s %s' % (self.player.name, self.year)


# All the possible league designs a user can enter
class League_Type(models.Model):
    contest = models.CharField(max_length=20)
    level = models.IntegerField(default=0)
    prize = models.DecimalField(max_digits=8, decimal_places=2)
    total_teams = models.CharField(max_length=20)

    def __str__(self):
        return '$%s %s %s' % (self.level, self.contest, self.id)

# All active leagues
class Leagues(models.Model):
    league_type = models.ForeignKey(League_Type, on_delete=models.CASCADE)
    winner = models.CharField(max_length=40,blank=True, null=True)
    filled = models.IntegerField(default=0)
    current = models.BooleanField(default=True)
    leauge_user = models.ManyToManyField(User, through='League_Users')
    players = models.ManyToManyField(Players, through='Rosters')

    def __str__(self):
        return '$%s %s %s' % (self.league_type.level, self.league_type.contest, self.id)

# Intermediate MTM table to track which users are in what league
class League_Users(models.Model):
    users = models.ForeignKey(User, on_delete=models.CASCADE)
    league = models.ForeignKey(Leagues, on_delete=models.CASCADE)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)
    team_name = models.CharField(max_length=40)
    bid = models.IntegerField(default=300, blank=True)
    number = models.IntegerField(default=0)

    def __str__(self):
        return '$%s %s %s' % (self.league.league_type.level, self.league.league_type.contest, self.users.username)

    class Meta:
        unique_together = (("users", "league"),)

# Full player list for each league, stated as roster so each player will have a roster attribute
class Rosters(models.Model):
    player = models.ForeignKey(Players, on_delete=models.CASCADE)
    leagues = models.ForeignKey(Leagues, on_delete=models.CASCADE)
    league_user = models.ForeignKey(League_Users, null=True, blank=True, on_delete=models.CASCADE)
    starting = models.BooleanField(default=False)
    drafted = models.BooleanField(default=False)

    class Meta:
        unique_together = (("player", "leagues"),)

    def __str__(self):
        return '%s league:%s user:%s' % (self.player.name, self.leagues.id, self.league_user.users.username)

class Rankings(models.Model):
    players = models.ManyToManyField(Players, through='Player_Rank')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=12, default='my rankings')
    league_type = models.CharField(max_length=10)

    def __str__(self):
        return '%s %s' % (self.user.username, self.league_type)


class Player_Rank(models.Model):
    player = models.ForeignKey(Players, on_delete=models.CASCADE)
    ranking_list = models.ForeignKey(Rankings, on_delete=models.CASCADE)
    ranking = models.IntegerField()

    def __str__(self):
        return '%s %s list:%s type:%s' % (self.ranking, self.player, self.ranking_list.user.username, self.ranking_list.league_type)


#class Podcasts(models.Model):
    #webm =
    #mp4 = model
    #mp3
