import requests
import json
import time
import sqlite3

connect = sqlite3.connect('database.db')
connect.execute('CREATE TABLE IF NOT EXISTS users(handle TEXT PRIMARY KEY, level INTEGER, matches INTEGER, score INTEGER, wins INTEGER, winrate FLOAT, kills INTEGER, kpg FLOAT)')

class user:
  handle : str = ''
  level : int = 0
  matches : int = 0
  score : int = 0
  wins : int = 0
  winrate : float = 0.0
  kills : int = 0
  kpg : float = 0.0

def getUserJSON(name):
  # set the API endpoint URL
  url = 'https://fortnite-api.com/v2/stats/br/v2'

  # set the API key for authentication (you will need to obtain this from the Fortnite Tracker website)
  payload = {
      'name': name,
      'accountType': 'epic',
      'timeWindow': 'season',
      'image': 'keyboardMouse'
  }
  headers = {
      'Authorization': #put your own API key here
  }

  # make the request to the API endpoint
  response = requests.get(url, params=payload, headers=headers)
  return response

def storeUserStats(user):
  with sqlite3.connect('database.db') as users:
    cursor = users.cursor()
    print("Adding user: " + user.handle)
    sql = "INSERT OR IGNORE INTO users(handle, level, matches, score, wins, winrate, kills, kpg) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(sql ,(user.handle, user.level, user.matches, user.score, user.wins,user.winrate, user.kills, user.kpg))
    sql = "UPDATE users SET level = ?, matches = ?, score = ?, wins = ?, winrate = ?, kills = ?, kpg = ? WHERE handle = ?"
    cursor.execute(sql ,(user.level, user.matches, user.score, user.wins,user.winrate, user.kills, user.kpg, user.handle))
    users.commit()

def setupNoStats(accountname):
    newUser = user()
    newUser.handle = accountname
    newUser.wins = -404
    return newUser


def setupPrivateStats(accountname):
    newUser = user()
    newUser.handle = accountname
    newUser.wins = -403
    return newUser

def getUserStats(response):
  # parse the JSON data into a Python dictionary
  data = json.loads(response.text)

  # set up new user instance
  newUser = user()
  newUser.handle = data["data"]["account"]["name"]
  newUser.level = data["data"]["battlePass"]["level"]
  newUser.matches = data["data"]["stats"]["all"]["overall"]["matches"]
  newUser.score = data["data"]["stats"]["all"]["overall"]["score"]
  newUser.wins = data["data"]["stats"]["all"]["overall"]["wins"]
  newUser.winrate = round(data["data"]["stats"]["all"]["overall"]["winRate"],2)
  newUser.kills = data["data"]["stats"]["all"]["overall"]["kills"]
  newUser.kpg = round(int(newUser.kills) / int(newUser.matches),2)

  return newUser

def getPlayers():
  f = open("players.txt")
  players = []
  for line in f:
    players.append(line.strip())
  return players

def updateDatabase():
  players = getPlayers()
  for player in players:
    print("Getting stats for: " + player)
    response = getUserJSON(player)
    #time.sleep(3)
    print("-- response code = ",response.status_code)
    if response.status_code == 200: # ok
      thisUser = getUserStats(response)
      storeUserStats(thisUser)
    elif response.status_code == 403: # private account
      thisUser = setupPrivateStats(player)
      storeUserStats(thisUser)
    elif response.status_code == 404: # no season data
      thisUser = setupNoStats(player)
      storeUserStats(thisUser)

if __name__ == '__main__':
    print("Started update at " + time.strftime('%Y-%m-%d %H:%M:%S'))
    updateDatabase()
    print("Finished update at " + time.strftime('%Y-%m-%d %H:%M:%S') + "\n\n")