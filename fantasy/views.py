from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic

from .models import *

# sends the current open league of each type
def index(request, page='Daily'):
    if request.method =='GET':
        context = {
        "leagues": Leagues.objects.filter(current=True).order_by('-league_type__prize').exclude(league_type__contest="Mock"),
        "page": page
        }
        return render(request, "fantasy/index.html", context)

#lists all leagues for the current user
def leagues(request):
    if request.method == 'GET':
        roster = Rosters.objects.filter(league_user__users=request.user, starting=True)
        context = {
            "leagues_user": League_Users.objects.filter(users=request.user).order_by('league__league_type__contest', '-league__league_type__level', 'number'),
            "lineup_qb": roster.filter(player__position='qb'),
            "lineup_rb": roster.filter(player__position='rb'),
            "lineup_wr": roster.filter(player__position='wr'),
            "lineup_te": roster.filter(player__position='te'),
            "lineup_k": roster.filter(player__position='k'),
            "lineup_d": roster.filter(player__position='d')
        }
        return render(request, "fantasy/leagues.html", context)

def research(request):
    if request.method =='GET':
        return render(request, "fantasy/mock.html")

def mock(request):
    # if this is a POST request we need to process the form data
    if request.method == 'GET':
        return render(request, "fantasy/mock.html")

def draft(request):
    if request.method == 'POST':
        user = request.user
        data = request.POST.copy()
        draft_status = data.get('draft')
        league_type = data.get('group1')
        scoring = data.get('group2')
        position = data.get('group3')
        rankings = Player_Rank.objects.filter(ranking_list__user__username='gboddie1', ranking_list__league_type=league_type).order_by('ranking')

        if draft_status == 'Mock':
            league_status = League_Type.objects.get(id=40)
            # create new league for mock draft
            new_league = Leagues(league_type=league_status)
            new_league.save()
            # add Free Agent user to hold unrostered players
            freeagent_user = League_Users(users.id='4', league=new_league, team_name='Free Agent')
            freeagent_user.save()
            # add user who is taking part in mock draft
            new_league_user = League_Users(users=user, league=new_league, team_name=user.username)
            new_league_user.save()


        for player in rankings:
            new_rostered_player = Rosters(player=player.player, leagues=new_league, league_user=freeagent_user)
            new_rostered_player.save()

        context = {
            "rankings": rankings,
            "picks": Player_Rank.objects.filter(ranking_list__user__username='gboddie1', ranking_list__league_type=league_type, ranking__range=(0, 6)).order_by('ranking'),
            "stats": Stats.objects.filter(year='2017'),
            "position": position,
            "league": new_league
        }
        return render(request, "fantasy/draft.html", context)
    else:
        return render(request, "fantasy/mock.html")

def podcasts(request):
    if request.method =='GET':
        context = {
        "leagues": Leagues.objects.filter(current=True, league_type__contest='Mock').order_by('-league_type__prize')
        }
    return render(request, "fantasy/mock.html", context)

#INDEX FUNCTION: adds new user to selected league and updates available openings
def new_league_user(request):
    if request.method == 'GET':
        leagueid = int(request.GET['leagueId'])
        userid = int(request.GET['userId'])
        username = request.GET['username']
        user = request.user
        contest = request.GET['contest']
        level = request.GET['level']

        old_league = Leagues.objects.get(id=leagueid)
        old_league.filled += 1
        old_league.save()

        if old_league.filled == 12:
            new_league = Leagues()
            new_league.league_type_id = old_league.league_type_id
            new_league.save()
            leagueid = int(new_league.id)
            old_league.current = False
            old_league.save()
            data = {
                "filled": new_league.filled,
                "teams": new_league.league_type.total_teams
            }
        else:
            data = {
                "filled": old_league.filled,
                "teams": old_league.league_type.total_teams
            }

        league_num = League_Users.objects.filter(users=user, league__league_type__contest=contest, league__league_type__level=level).count() + 1
        league = Leagues.objects.get(id=leagueid)
        new = League_Users(users=user, league=league, team_name=username, number=league_num)
        new.save()

        return JsonResponse(data)

def update_fieldset(request):
    if request.method == 'GET':
        # full list of players in specific rankings
        player_list = request.GET.getlist('player_list[]')
        position_list = request.GET.getlist('position_list[]')
        stat_list = request.GET.getlist('stat_list[]')
        leagueid = int(request.GET['leagueid'])
        player_copy = []
        position_copy = []
        stat_copy = []

        for player in player_list:
            player_copy.append(player)

        for pos in position_list:
            position_copy.append(pos)

        for stat in stat_list:
            stat_copy.append(stat)

        league = Leagues.objects.get(id=leagueid)
        league_roster = Rosters.objects.filter(leagues=league, drafted=True)

        for i in range(0, len(player_list)):
            for drafted in league_roster:
                if player_list[i] == drafted.player.name:
                    player_copy.remove(player_list[i])
                    position_copy.remove(position_list[i])
                    stat_copy.remove(stat_list[i])

        data = {
        "names": player_copy[:5],
        "position": position_copy[:5],
        "stats": stat_copy[:5]
        }
        return JsonResponse(data)

def drafted_player(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        league_id = int(request.GET.get('league_id'))
        user = request.user

        draftee_player = Rosters.objects.get(player__name=name,leagues__id=league_id)
        print(draftee_player.player.name)
        # searching for specific user for specific league
        league_user = League_Users.objects.get(users=user, league__id=league_id)
        # assigning drafted player to a specific team
        draftee_player.league_user = league_user
        # taking player away from draftable list
        draftee_player.drafted = True
        draftee_player.save()
        # returning all players currently drafted for this user in this league
        users_roster = Rosters.objects.filter(league_user=league_user)

        count = 0
        for player in users_roster:
            # checking for the number of players drafted at this players position
            if player.player.position == draftee_player.player.position:
                count += 1

        #assigning starters
        if draftee_player.player.position == 'QB' and count == 1:
            draftee_player.starting = True
        elif draftee_player.player.position == 'RB' and count <= 2:
            draftee_player.starting = True
        elif draftee_player.player.position == 'WR' and count <= 2:
            draftee_player.starting = True
        elif draftee_player.player.position == 'TE' and count == 1:
            draftee_player.starting = True
        elif draftee_player.player.position == 'DST' and count == 1:
            draftee_player.starting = True



        data = {
        "name": name,
        "position": draftee_player.player.position,
        "starting": draftee_player.starting,
        }
        return JsonResponse(data)
