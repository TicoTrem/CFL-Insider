
from operator import itemgetter
import time
import requests
import datetime

import sys


BASE_URL = "https://api.the-odds-api.com/v4/sports"
API_KEY = sys.argv[1]
SPORT_NAME = "/americanfootball_cfl"

def get_average_total_points_of_game(game):
    total_points_sum = 0

    # if the game does not have bookmaker data
    if not game['bookmakers']:
        return None

    for bookmaker in game['bookmakers']:
        for market in bookmaker['markets']:
            over = market['outcomes'][0]['point']
            under = market['outcomes'][1]['point']
            if over == under:
                total_points_sum += over
            else:
                raise ArithmeticError(f"For some reason {bookmaker['title']} has different values for over({over}) and under({under})")
    average_total_points = total_points_sum / len(game['bookmakers'])
    return round(average_total_points)


def get_average_home_weightings(game):
    home_sum = 0

    # if the game does not have bookmaker data
    if not game['bookmakers']:
        return None
    
    for bookmaker in game['bookmakers']:
        # the home and away markets seem to change order, have to check
        market1 = bookmaker['markets'][0]['outcomes'][0]
        market2 = bookmaker['markets'][0]['outcomes'][1]

        # if its the home market, add its points to the home sum
        # else add the other markets points to the home sum
        # hopefully there are only ever 2 markets
        if market1['name'] == game['home_team']:
            home_sum += market1['point']
        else:
            home_sum += market2['point']
    # game_dict['total_points'] = get_total_points_for_game(spread_game)
    if game['bookmakers']:
        return home_sum / len(game['bookmakers'])
    

def get_dict_list(num_games):

    spreads_response = requests.get(f"{BASE_URL}{SPORT_NAME}/odds?apiKey={API_KEY}&regions=uk,us,us2,eu,au&markets=spreads&date={datetime.datetime.now().isoformat}CST&all=true")
    spreads_json_data = spreads_response.json()

    totals_response = requests.get(f"{BASE_URL}{SPORT_NAME}/odds?apiKey={API_KEY}&regions=uk,us,us2,eu,au&markets=totals&date={datetime.datetime.now().isoformat}CST&all=true")
    totals_json_data = totals_response.json()

    if num_games > len(spreads_json_data):
        num_games = len(spreads_json_data)

    results = []


    for nGame in range(0,num_games):
        game_dict = {}
        
        spread_game = spreads_json_data[nGame]
        totals_game = totals_json_data[nGame]

        game_dict['id'] = spread_game['id']
        game_dict['home'] = spread_game['home_team']
        game_dict['away'] = spread_game['away_team']

        game_dict['home_average'] = get_average_home_weightings(spread_game)
        game_dict['total_points'] = get_average_total_points_of_game(totals_game)
        
        # if any of these are none, then don't add it to the results dict
        if not game_dict['home_average'] or not game_dict['total_points']:
            continue

        results.append(game_dict)

    return results


# Returns a string to send as a discord message to the user
def get_rankings(home_game_average_list):
    # [{id:2o34823, home: roughriders, away: stampeders, home_average: -5.3}, {...}]
    new_list = sorted(home_game_average_list, key=lambda d: abs(d['home_average']))

    return_string = ""
    # loop through original list to preserve the order by soonest game
    for game in home_game_average_list:
        game['priority'] = new_list.index(game) + 1

        # home won
        if game['home_average'] < 0:
            winner = game['home']
        # away won
        else:
            winner = game['away']

        return_string += f"**{game['home']} vs {game['away']}**\n\tWinner: *{winner}*\n\tPriority: *{game['priority']}*\n\tGame total points: *{game['total_points']}*\n"
    return return_string


# performs the whole shebang, returns the string to send to the user on discord
def get_insider_data(num_games):
    dict_list = get_dict_list(num_games)
    return_string = get_rankings(dict_list)
    return return_string



import discord
from discord.ext import commands, tasks
import asyncio

DISCORD_TOKEN = sys.argv[2]

intents = discord.Intents.default()
intents.messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

user_id = 248942568480571393

reacted = True


@tasks.loop(hours=1)
async def spam_to_update_picks():
    global reacted
    if reacted == False:
        user = await bot.fetch_user(user_id)
        await user.send("Bro... You didn't react to a message to signal your picks are up to date. Please do that...")


@tasks.loop(hours=24)
async def get_the_daily_scoop():
    global reacted
    if bot.is_ready():
        user = await bot.fetch_user(user_id)
        msg = "Hello, this is your daily reminder to update your picks!\n"
        msg += "Here is a link to update them: https://www.pooltracker.com/w/season/picks_edit.asp?poolid=232361\n"
        msg += "please enter the number of games displayed for this week (Even the completed games)"

        await user.send(msg)
        reacted = False
        



@get_the_daily_scoop.before_loop
async def before_daily_task():
    await asyncio.sleep(get_delay(7, 0))
    
@spam_to_update_picks.before_loop
async def before_daily_task():
    # starts a little bit before the daily scoop so that it doesn't
    # check if you reacted until around an hour
    await asyncio.sleep(get_delay(6, 55))

def get_delay(start_hour, start_minute):
    # Calculate the initial delay until the next target time
    now = datetime.datetime.now()
    target_time = datetime.datetime.combine(now.date(), datetime.time(hour=start_hour, minute=start_minute))
    if now > target_time:
        # If the current time is past the target time, schedule for tomorrow
        target_time += datetime.timedelta(days=1)
    initial_delay = (target_time - now).total_seconds()


@bot.event
async def on_message(message):
    
    if message.author == bot.user:
        return

    # no guild = dm
    try:
        num = int(message.content)
    except:
        await message.channel.send("That couldn't be parsed in to an int")
        return
    
    if message.guild is None:
        await message.channel.send(get_insider_data(num) + "\n\n**If there are differences from the last time you submitted your picks, please update those now**")

@bot.event
async def on_raw_reaction_add(payload):
    global reacted
    print("got the reaction")
    user_id = payload.user_id
    print(user_id)
    user = await bot.fetch_user(user_id)
    if not user:
        print("The user aint working")
    await user.send("Confirming I got your reaction")
    reacted = True
    

@bot.event
async def on_ready():
    spam_to_update_picks.start()
    time.sleep(1)
    get_the_daily_scoop.start()
    


    


bot.run(DISCORD_TOKEN)