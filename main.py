from operator import itemgetter
import requests
import datetime

print("Hello World")
BASE_URL = "https://api.the-odds-api.com/v4/sports"
API_KEY = "dc2b3ae29e6afb5a4ca7ab9dbdd6d2ad"
SPORT_NAME = "/americanfootball_cfl"

def get_total_points_for_game(game):
    for game in totals_json_data:
        print(f"The game is {game['home_team']} vs. {game['away_team']}")
        for bookmaker in game['bookmakers']:
            for market in bookmaker['markets']:
                over = market['outcomes'][0]['point']
                under = market['outcomes'][1]['point']
                if over == under:
                    print(f"{bookmaker['title']} thinks that the total points are going to be {over}")
                else:
                    print(f"For some reason {bookmaker['title']} has different values for over({over}) and under({under})")
    return

def get_average_home_points_dict_list(num_games, spreads_json_data):
    results = []

    for nGame in range(0,num_games):
        game_dict = {}
        game = spreads_json_data[nGame]
        game_dict['id'] = game['id']
        game_dict['home'] = game['home_team']
        game_dict['away'] = game['away_team']

        home_sum = 0
        print(f"The game is {game_dict['home']} vs. {game_dict['away']}")
        bookmaker_count = 0
        for bookmaker in game['bookmakers']:
            # the home and away markets seem to change order, have to check
            market1 = bookmaker['markets'][0]['outcomes'][0]
            market2 = bookmaker['markets'][0]['outcomes'][1]

            # if its the home market, add its points to the home sum
            # else add the other markets points to the home sum
            # hopefully there are only ever 2 markets
            if market1['name'] == game_dict['home']:
                home_sum += market1['point']
            else:
                home_sum += market2['point']
            bookmaker_count += 1

        game_dict['home_average'] = home_sum / bookmaker_count
        results.append(game_dict)
    return results


def get_rankings(home_game_average_list):
    # [{id:2o34823, home: roughriders, away: stampeders, home_average: -5.3}, {...}]
    print(home_game_average_list)
    new_list = sorted(home_game_average_list, key=lambda d: abs(d['home_average']))
    print(new_list)



    for game in home_game_average_list:
        game['priority'] = new_list.index(game) + 1

        # home won
        if game['home_average'] < 0:
            winner = game['home']
        # away won
        else:
            winner = game['away']

        print(f"{game['home']} vs {game['away']}\tWinner: {winner}\tPriority: {game['priority']}")


def print_insider_data(num_games):
    spreads_response = requests.get(f"{BASE_URL}{SPORT_NAME}/odds?apiKey={API_KEY}&regions=uk,us,us2,eu,au&markets=spreads&date={datetime.datetime.now().isoformat}CST&all=true")
    spreads_json = spreads_response.json()
    dict_list = get_average_home_points_dict_list(num_games, spreads_json)

    




# response = requests.get(f"{BASE_URL}?apiKey={API_KEY}&all=false")
# response = requests.get("https://api.the-odds-api.com/v4/sports/americanfootball_cfl/odds?apiKey=" + API_KEY + "&all=true")
# response = requests.get("https://api.the-odds-api.com/v4/sports/americanfootball_cfl/odds?apiKey=dc2b3ae29e6afb5a4ca7ab9dbdd6d2ad&regions=us&markets=totals&dateFormat=iso&oddsFormat=decimal&date=2024-06-20T12%3A15%3A00CST&all=true")
# response = requests.get(f"{BASE_URL}{SPORT_NAME}/odds?apiKey={API_KEY}&regions=uk,us,us2,eu,au&markets=totals&date={datetime.datetime.now().isoformat}CST&all=true")
response = requests.get(f"{BASE_URL}{SPORT_NAME}/odds?apiKey={API_KEY}&regions=uk,us,us2,eu,au&markets=spreads&date={datetime.datetime.now().isoformat}CST&all=true")
# print(response)
json_data = response.json()
# print(json_data)
# print_total_point_data(json_data)
game_points_list = get_average_home_points_dict_list(4,json_data)
get_rankings(game_points_list)

print_insider_data(4)



