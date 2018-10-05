from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import generic
import random
import json

from .models import *

# sends the current open league of each type
#single template for four pages
def index(request, page='Daily'):
    if request.method =='GET':
        context = {
        "leagues": Leagues.objects.filter(current=True).order_by('-league_type__prize').exclude(league_type__contest="Mock"),
        "page": page
        }
        return render(request, "fantasy/index.html", context)

#INDEX FUNCTION: adds new user to selected league and updates available openings
def new_league_user(request):
    if request.method == 'GET':
        leagueid = int(request.GET['leagueId'])
        userid = int(request.GET['userId'])
        username = request.GET['username']
        user = request.user
        contest = request.GET['contest']
        level = request.GET['level']
        in_league = League_Users.objects.filter(league__id=leagueid, users=user)
        #checks if user already in league
        if in_league.count() > 0:

            data = {"error": 'already in league'}

            return JsonResponse(data)
        else:
            #add to current league
            old_league = Leagues.objects.get(id=leagueid)
            old_league.filled += 1
            old_league.save()
            #assign user position in league
            leagues_of_type = League_Users.objects.filter(users=user, league__league_type__contest=old_league.league_type.contest, league__league_type__level=old_league.league_type.level).count() + 1
            franchise_bought = League_Users.objects.get(users_id='4', league=old_league, franchise=old_league.filled)
            franchise_bought.users = user
            franchise_bought.team_name = username
            franchise_bought.number = leagues_of_type
            franchise_bought.save()

            #if league is filled create new instance of league
            if old_league.filled == 12:
                new_league = Leagues()
                new_league.league_type_id = old_league.league_type_id
                new_league.save()
                #populate new league with stand in franchises until purchased by user
                for i in range(1, 13):
                    new_league_user = League_Users(users_id='4', league=new_league, team_name='Franchise ' + str(i), franchise=i)
                    new_league_user.save()

                old_league.current = False
                old_league.save()
                # get all league users
                all_users = League_Users.objects.filter(league=old_league).exclude(users_id='4')
                list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
                # make their order random
                random.shuffle(list)
                count = 0
                # give random ordered list draft positions
                for owner in all_users:
                    owner.draft_position = list[count]
                    count += 1
                # user for all free agents
                freeagent_user = League_Users(users_id='4', league=new_league, team_name='Free Agent')
                freeagent_user.save()
                rankings = Player_Rank.objects.filter(ranking_list__user__username='gboddie1', ranking_list__league_type=old_league.league_type.contest).order_by('ranking')

                # go through ranking list and add all available players to free agent user
                for player in rankings:
                    new_rostered_player = Rosters(player=player.player, leagues=new_league, league_user=freeagent_user)
                    new_rostered_player.save()

                data = {
                    "filled": new_league.filled,
                    "teams": new_league.league_type.total_teams
                }
            else:
                data = {
                    "filled": old_league.filled,
                    "teams": old_league.league_type.total_teams
                }

            return JsonResponse(data)

#lists all leagues for the current user in order
def leagues(request):
    if request.method == 'GET':
        roster = Rosters.objects.filter(league_user__users=request.user, starting=True).exclude(leagues__league_type__contest='Mock')
        context = {
            "user_leagues": League_Users.objects.filter(users=request.user).order_by('league__league_type__contest', '-league__league_type__level', 'number').exclude(league__league_type__contest='Mock'),
            "lineup_QB": roster.filter(player__position='QB'),
            "lineup_RB": roster.filter(player__position='RB'),
            "lineup_WR": roster.filter(player__position='WR'),
            "lineup_TE": roster.filter(player__position='TE'),
            "lineup_DST": roster.filter(player__position='DST'),
            "roster": roster
        }
        return render(request, "fantasy/leagues.html", context)
#page not developed no research articles to populate
def research(request):
    if request.method =='GET':
        return render(request, "fantasy/research.html")
#draft against automated system for practice
def mock(request):
    # if this is a POST request we need to process the form data
    if request.method == 'GET':
        return render(request, "fantasy/mock.html")
#page not populated dont have podcast files to populate
def podcasts(request):
    if request.method =='GET':
        context = {
        "leagues": Leagues.objects.filter(current=True, league_type__contest='Mock').order_by('-league_type__prize')
        }
    return render(request, "fantasy/podcast.html", context)
#post requested function populated by data from mock function
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
            freeagent_user = League_Users(users_id='4', league=new_league, team_name='Free Agent')
            freeagent_user.save()
            # add user who is taking part in mock draft
            new_league_user = League_Users(users=user, league=new_league, team_name=user.username)
            new_league_user.save()

        # go through ranking list and add all available players to free agent user
        for player in rankings:
            new_rostered_player = Rosters(player=player.player, leagues=new_league, league_user=freeagent_user)
            print('ranking' + str(player.ranking))
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
        return redirect(mock)
#home page for each unique league
def leaguehome(request, leagueid):
    if request.method =='GET':
        user = request.user
        league = Leagues.objects.get(id=leagueid)
        league_user = League_Users.objects.get(league=league, users=user)
        roster = Rosters.objects.filter(leagues=league, league_user=league_user).order_by('-starting')
        all_leagues = League_Users.objects.filter(users=user).order_by('league__league_type__contest', '-league__league_type__level', 'number').exclude(league__league_type__contest='Mock')

        context = {
        "roster": roster,
        "standings": League_Users.objects.filter(league=league).order_by('-wins', 'loses').exclude(team_name='Free Agent'),
        "all_leagues": all_leagues,
        "league": league,
        "league_user": league_user
        }

        return render(request, 'fantasy/leaguehome.html', context)
#page of all rosters in a league
def leaguerosters(request, leagueid):
    if request.method == 'GET':
        league = Leagues.objects.get(id=leagueid)
        all_users = League_Users.objects.filter(league=league).exclude(team_name='Free Agent')
        roster = Rosters.objects.filter(leagues=league).order_by('-starting').exclude(league_user__users_id='4')
        fantasy_points = Fantasy_Points.objects.filter(year='2018')

        context = {
        "league": league,
        "all_users": all_users,
        "roster": roster,
        "fantasy_points": fantasy_points
        }
        return render(request, 'fantasy/leaguerosters.html', context)
#page of all players in a league given sorting options
def leagueplayers(request, leagueid):
    if request.method == 'GET':
        league = Leagues.objects.get(id=leagueid)
        free_agents = Rosters.objects.filter(league_user__users_id='4', leagues=league).exclude(player__position='DST')
        nfl_teams = Teams.objects.all().order_by('mascot')
        fantasy_points = Fantasy_Points.objects.filter(year=2018)
        stats = Stats.objects.filter(year=2018)
        all_users = League_Users.objects.filter(league=league).exclude(users_id='4')

        context = {
        "league": league,
        "free_agents": free_agents,
        "nfl_teams": nfl_teams,
        "fantasy_points": fantasy_points,
        "stats": stats,
        "all_users":all_users
        }
        return render(request, 'fantasy/leagueplayers.html', context)
#LEAGUEPLAYERS FUNCTION: sorting function that filters players of a league based on user selections
def change(request):
    if request.method == 'GET':
        league_id = int(request.GET.get('leagueid'))
        status = request.GET.get('status')
        position = request.GET.get('position')
        team = request.GET.get('team')
        league = Leagues.objects.get(id=league_id)
        players = Rosters.objects.filter(leagues=league)
        fantasy_points = Fantasy_Points.objects.filter(year=2018)
        stats = Stats.objects.filter(year=2018)

        if status == 'Free Agents':
            players = players.filter(league_user__users_id='4')

        elif status != 'Free Agents' and status != 'All Players':
            league_user = League_Users.objects.get(league=league, team_name = status)
            players = players.filter(league_user=league_user)

        if position == 'Offense':
            players = players.exclude(player__position='DST')

        else:
            players = players.filter(player__position=position)

        if team != 'All':
            players = players.filter(player__team__mascot=team)

        playerlist = []
        pointslist = []
        statlist = []
        r_dict = {}
        f_dict = {}
        s_dict = {}

        for player in players:
            r_dict = {
                'name': player.player.name,
                'bye': player.player.bye_week,
                'owner': player.league_user.team_name
            }
            playerlist.append(r_dict)

        for points in fantasy_points:
            f_dict = {
                'name': points.player.name,
                'total': points.total_points,
            }
            pointslist.append(f_dict)

        # only getting offensive stats dont have a template for defensive
        for stat in stats:
            s_dict = {
                'name': stat.player.name,
                'passing_yards': stat.passing_yards,
                'passing_tds': stat.passing_tds,
                'passing_interceptions': stat.passing_interceptions,
                'rushing_yards': stat.rushing_yards,
                'rushing_tds': stat.rushing_tds,
                'catches': stat.catches,
                'receiving_yards': stat.receiving_yards,
                'receiving_tds': stat.receiving_tds,
                'return_tds': stat.return_tds,
                'two_pt': stat.two_pt,
                'fumbles': stat.fumbles
            }
            statlist.append(s_dict)



        data = {
        "players": json.dumps(playerlist),
        "fantasy_points": json.dumps(pointslist),
        "stats": json.dumps(statlist)
        }
        return JsonResponse(data)
#all roster changes from this league
def leaguetransactions(request, leagueid):
    if request.method =='GET':
        league = Leagues.objects.get(id=leagueid)
        transactions = Transactions.objects.filter(league=league).order_by('-date')

        context = {
        "league": league,
        "transactions": transactions
        }
        return render(request, 'fantasy/leaguetransactions.html', context)
#sets starting lineup in this league for current user
def leaguelineup(request, leagueid):
    if request.method == 'GET':
        league = Leagues.objects.get(id=leagueid)
        league_user = League_Users.objects.get(league=league, users=request.user)
        roster = Rosters.objects.filter(leagues=league, league_user=league_user).order_by('-starting')
        fantasy_points = Fantasy_Points.objects.filter(year='2018')

        context = {
        "league": league,
        "roster": roster,
        "fantasy_points": fantasy_points,
        "league_user": league_user
        }
        return render(request, 'fantasy/leaguelineup.html', context)
#LEAGUELINEUP FUNCTION: starting position swap for leaguehome and leaguelineup
def swap(request):
    if request.method == 'GET':
        league_user_id = int(request.GET.get('league_user_id'))
        league_user = League_Users.objects.get(id=league_user_id)
        id = request.GET.get('id')
        otherid = request.GET.get('otherid')
        first = Rosters.objects.get(player_id=id, league_user=league_user)
        second = Rosters.objects.get(player_id=otherid, league_user=league_user)
        first.starting = not first.starting
        first.save()
        second.starting = not second.starting
        second.save()


        data = {
        "success": 'true'
        }
        return JsonResponse(data)
#draft page for this league will have different states pre and post draft
def leaguedraft(request, leagueid):
    if request.method == 'GET':
        user = request.user
        league = Leagues.objects.get(id=leagueid)
        league_user = League_Users.objects.get(league=league, users=user)
        all_users = League_Users.objects.filter(league=league)
        rankings = Player_Rank.objects.filter(ranking_list__user__username='gboddie1', ranking_list__league_type=league.league_type.contest).order_by('ranking')

        context = {
            "all_users": all_users,
            "league_user": league_user,
            "league": league,
            "stats": Stats.objects.filter(year='2017'),
            "rankings": rankings
        }

        return render(request, 'fantasy/leaguedraft.html', context)
#DRAFT FUNCTION: ajax function updates fieldset area to highest rated available players
def update_fieldset(request):
    if request.method == 'GET':
        # full list of players in specific rankings
        player_list = request.GET.getlist('player_list[]')
        position_list = request.GET.getlist('position_list[]')
        ranking_list = request.GET.getlist('ranking_list[]')
        stat_list = request.GET.getlist('stat_list[]')
        leagueid = int(request.GET.get('leagueid'))
        player_copy = player_list.copy()
        position_copy = position_list.copy()
        ranking_copy = ranking_list.copy()
        stat_copy = stat_list.copy()

        league = Leagues.objects.get(id=leagueid)
        league_roster = Rosters.objects.filter(leagues=league, drafted=True)
        # remove drafted players from list copies and return them in ranked order
        for i in range(0, len(player_list)):
            for drafted in league_roster:
                if player_list[i] == drafted.player.name:
                    player_copy.remove(player_list[i])
                    position_copy.remove(position_list[i])
                    ranking_copy.remove(ranking_list[i])
                    #stat_copy.remove(stat_list[i])

        data = {
        "names": player_copy[:5],
        "position": position_copy[:5],
        "ranking": ranking_copy[:5],
        "stats": stat_copy[:5]
        }
        return JsonResponse(data)
#DRAFT FUNCTION: ajax function updating database drafted players
def drafted_player(request):
    if request.method == 'GET':
        name = request.GET.get('name')
        league_id = int(request.GET.get('league_id'))
        user = request.user

        draftee_player = Rosters.objects.get(player__name=name, leagues__id=league_id)
        # searching for specific user for specific league
        if(draftee_player.drafted == True):
            data = {
            "error": 'Player already drafted'
            }
            return JsonResponse(data)

        league_user = League_Users.objects.get(users=user, league__id=league_id)
        # assigning drafted player to a specific team
        draftee_player.league_user = league_user
        # taking player away from draftable list
        draftee_player.drafted = True
        draftee_player.save()
        # all players currently drafted for this user in this league
        user_roster = Rosters.objects.filter(league_user=league_user, leagues__id=league_id)

        count = 0
        for player in user_roster:
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
        "starting": draftee_player.starting
        }
        return JsonResponse(data)
#DRAFT FUNCTION: mock draft it auto picks all other pick not made by user_roster
#leaguedraft auto picks players when available time runs out
def auto(request):
    if request.method == 'GET':
        # full list of players in and ordered rank
        player_list = request.GET.getlist('player_list[]')
        # id for current league
        league_id = int(request.GET.get('league_id'))
        # current user
        league_user = League_Users.objects.get(users_id='4', league__id=league_id)

        # all free agents in this league
        free_agents = Rosters.objects.filter(leagues_id=league_id, league_user__users_id='4', drafted=False) # 4 is the user id for all free agents

        count = 0
        # outer loop is holding the ranking order inner loop is current free agents
        for player in player_list:
            count += 1
            for agent in free_agents:
                if player == agent.player.name: # 20% randomization for next drafted player
                    name = agent.player.name
                    position = agent.player.position
                    agent.league_user = league_user
                    user = agent.league_user
                    agent.drafted = True
                    agent.save()
                    break
            else:
                continue # only executed if the inner loop did not break
            break # only executed if the inner loop did break

        data = {
        "ranking": count,
        "name": name,
        "position": position
        }
        return JsonResponse(data)
#DRAFT FUNCTION: checks every 2 seconds for change in drafted players in database
#ALTERNATE TO WEB SOCKETS WHICH ARENT NATIVE IN DJANGO
def keep_current(request):
    if request.method == 'GET':
        round = request.GET.get('round')
        current_pick = request.GET.get('current_pick')
        active_list = request.GET.getlist('activelist[]')
        leagueid = request.GET.get('leagueid')
        active_copy = active_list.copy()
        # all free agents in this league
        roster = Rosters.objects.filter(leagues_id=leagueid)
        count = 0
        ranking = []
        names = []
        position = []
        #checking if current available players changes
        for player in active_list:
            for person in roster:
                if player == person.player.name and person.drafted == True:
                    active_copy.remove(player)
                    player_rank = Player_Rank.objects.get(player__name=player, ranking_list__user__username='gboddie1', )
                    ranking.append(player_rank.rank)
                    names.append(player)
                    position.append(person.player.position)
                    count += 1

        if count > 0:
            current_pick += count
            round = current_pick // 12

            data = {
            "activelist": active_copy,
            "current_pick": current_pick,
            "round": round,
            "ranking": ranking,
            "names": names,
            "position": position
            }
        else:
            data = {
            "noChange": 'none'
            }
        return JsonResponse(data)
#DRAFT FUNCTION: updates draft page if opened after draft begins
def update_drafted_players(request):
    if request.method == 'GET':
        leagueid = int(request.GET.get('leagueid'))
        # full list of players in specific rankings
        player_list = request.GET.getlist('player_list[]')
        position_list = request.GET.getlist('position_list[]')
        ranking_list = request.GET.getlist('ranking_list[]')
        roster = Rosters.objects.filter(leagues__id=leagueid)
        player_drafted = []
        position_drafted = []
        ranking_drafted = []
        #list of drafted players in this league
        for player in roster:
            for i in range(0, len(player_list)):
                if player.player.name == player_list[i] and player.drafted == True:
                    player_drafted.append(player_list[i])
                    position_drafted.append(position_list[i])
                    ranking_drafted.append(ranking_list[i])

        data = {
        'players': player_drafted,
        'positions': position_drafted,
        'rankings': ranking_drafted
        }
        return JsonResponse(data)

#calendar for all league events
def leaguecalendar(request, leagueid):
    if request.method == 'GET':
        league = Leagues.objects.get(id=leagueid)

        context = {
        "league": league
        }
        return render(request, 'fantasy/leaguecalendar.html', context)
