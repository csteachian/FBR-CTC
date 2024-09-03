from flask import Flask, request
from flask import render_template
import sqlite3
import pathlib, datetime
import subprocess

app = Flask(__name__)

connect = sqlite3.connect('fbr/database.db')
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


def getUsersFromDatabase():
  users = []

  conn = sqlite3.connect('fbr/database.db')
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM users")
  data = cursor.fetchall()
  for item in data:
    thisUser = user()
    thisUser.handle = item[0]
    thisUser.level = item[1]
    thisUser.matches = item[2]
    thisUser.score = item[3]
    thisUser.wins = item[4]
    thisUser.winrate = item[5]
    thisUser.kills = item[6]
    thisUser.kpg = item[7]
    users.append(thisUser)

  return users

def sortusers(users, category):
  if category == 'wins':
    return sorted(users, key=lambda user: (user.wins, user.winrate), reverse=True)
  elif category == 'matches':
    return sorted(users, key=lambda user: (user.matches, user.winrate), reverse=True)
  elif category == 'score':
    return sorted(users, key=lambda user: (user.score, user.winrate), reverse=True)
  elif category == 'kills':
    return sorted(users, key=lambda user: (user.kills, user.winrate), reverse=True)
  elif category == 'kpg':
    return sorted(users, key=lambda user: (user.kpg, user.winrate), reverse=True)
  elif category == 'winrate':
    return sorted(users, key=lambda user: (user.winrate, user.matches), reverse=True)

@app.route('/')
def index():
  users = []
  outputHTML = ""

  sortType = request.args.get('s')
  if sortType == None:
    sortType = "wins"

  users = getUsersFromDatabase()
  users = sortusers(users, sortType)

  fname = pathlib.Path('fbr/database.db')
  modifiedTS = datetime.datetime.fromtimestamp(fname.stat().st_mtime, tz=datetime.timezone.utc)

  outputHTML = render_template('index.html', users=users, sortType = sortType, modifiedTS = modifiedTS)
  return outputHTML

@app.route('/update')
def update():
    cmd = 'cd fbr; python update.py'
    returncode = subprocess.call(cmd, shell=True)
    outputHTML = render_template('update.html', returncode = returncode)
    return outputHTML

# Commented out because I host this on pythonanywhere.com
#if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=False)