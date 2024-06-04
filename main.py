import requests
import datetime

print("Hello World")
BASE_URL = "https://api.the-odds-api.com/v4/sports"
API_KEY = "dc2b3ae29e6afb5a4ca7ab9dbdd6d2ad"
SPORT_NAME = "/americanfootball_cfl"
# response = requests.get(f"{BASE_URL}?apiKey={API_KEY}&all=false")
# response = requests.get("https://api.the-odds-api.com/v4/sports/americanfootball_cfl/odds?apiKey=" + API_KEY + "&all=true")
# response = requests.get("https://api.the-odds-api.com/v4/sports/americanfootball_cfl/odds?apiKey=dc2b3ae29e6afb5a4ca7ab9dbdd6d2ad&regions=us&markets=totals&dateFormat=iso&oddsFormat=decimal&date=2024-06-20T12%3A15%3A00CST&all=true")
response = requests.get(f"{BASE_URL}{SPORT_NAME}/odds?apiKey={API_KEY}&regions=us,us2&markets=totals&date={datetime.datetime.now().isoformat}CST&all=true")
print(response)
json_data = response.json()
print(json_data)
for game in json_data:
    print(f"The game is {game['home_team']} vs. {game['away_team']}")
    for bookmaker in game['bookmakers']:
        for market in bookmaker['markets']:
            over = market['outcomes'][0]['point']
            under = market['outcomes'][1]['point']
            if over == under:
                print(f"{bookmaker['title']} thinks that the total points are going to be {over}")
            else:
                print(f"For some reason {bookmaker['title']} has different values for over({over}) and under({under})")

