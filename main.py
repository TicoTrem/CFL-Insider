from operator import itemgetter
import requests
import datetime

BASE_URL = "https://api.the-odds-api.com/v4/sports"
API_KEY = "31a579d1084fc35eab5070dfa28ea781"
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
    return average_total_points


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

        return_string += f"{game['home']} vs {game['away']}\tWinner: {winner}\tPriority: {game['priority']}\tGame total points: {game['total_points']}\n"
    return return_string


# performs the whole shebang, returns the string to send to the user on discord
def get_insider_data(num_games):
    dict_list = get_dict_list(num_games)
    return_string = get_rankings(dict_list)
    return return_string



    
game_points_list = get_dict_list(4)
get_rankings(game_points_list)

print(get_insider_data(10))


