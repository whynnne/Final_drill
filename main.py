from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "leagues"
mysql = MySQL(app)

def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

@app.route("/")
def hello_world():
    return "WELCOME TO THE LEAGUES DATABASE"

@app.route("/leagues")
def get_leagues():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Leagues")
    leagues = cursor.fetchall()
    if not leagues:
        return handle_error("No leagues found", 404)

    leagues_list = [
        {
            "league_ID": league[0], 
            "name": league[1],
            "country": league[2]
        }
        for league in leagues
    ]
    
    return jsonify(leagues_list), 200

@app.route("/teams")
def get_teams():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Teams")
    teams = cursor.fetchall()
    if not teams:
        return handle_error("No teams found", 404)

    teams_list = [
        {
            "team_ID": team[0], 
            "name": team[1], 
            "league_ID": team[2]
        }
        for team in teams
    ]
    
    return jsonify(teams_list), 200

@app.route("/players")
def get_players():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Players")
    players = cursor.fetchall()
    if not players:
        return handle_error("No players found", 404)

    players_list = [
        {
            "player_ID": player[0], 
            "name": player[1], 
            "age": player[2], 
            "position": player[3], 
            "team_ID": player[4]
        }
        for player in players
    ]
    
    return jsonify(players_list), 200

@app.route("/matches")
def get_matches():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Matches")
    matches = cursor.fetchall()
    if not matches:
        return handle_error("No matches found", 404)

    matches_list = [
        {
            "match_ID": match[0],
            "home_team_ID": match[1], 
            "away_team_ID": match[2], 
            "date": match[3], 
            "home_score": match[4], 
            "away_score": match[5]
        }
        for match in matches
    ]
    
    return jsonify(matches_list), 200

@app.route("/leagues", methods=["POST"])
def add_league():
    data = request.get_json()
    league_id = data.get('league_ID')
    name = data.get('name')
    country = data.get('country')

    if not all([league_id, name, country]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Leagues (League_ID, Name, Country) VALUES (%s, %s, %s)", 
        (league_id, name, country)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Leagues WHERE League_ID = %s", (league_id,))
    league = cursor.fetchone()

    if not league:
        return handle_error("Failed to retrieve the added league", 500)

    return jsonify({
        "league_ID": league[0], 
        "name": league[1],
        "country": league[2]
    }), 201

@app.route("/teams", methods=["POST"])
def add_team():
    data = request.get_json()
    team_id = data.get('team_ID')
    name = data.get('name')
    league_id = data.get('league_ID')

    if not all([team_id, name, league_id]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Teams (Team_ID, Name, League_ID) VALUES (%s, %s, %s)", 
        (team_id, name, league_id)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Teams WHERE Team_ID = %s", (team_id,))
    team = cursor.fetchone()

    if not team:
        return handle_error("Failed to retrieve the added team", 500)

    return jsonify({
        "team_ID": team[0], 
        "name": team[1], 
        "league_ID": team[2]
    }), 201

@app.route("/players", methods=["POST"])
def add_player():
    data = request.get_json()
    player_id = data.get('player_ID')
    name = data.get('name')
    age = data.get('age')
    position = data.get('position')
    team_id = data.get('team_ID')

    if not all([player_id, name, age, position, team_id]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Players (Player_ID, Name, Age, Position, Team_ID) VALUES (%s, %s, %s, %s, %s)", 
        (player_id, name, age, position, team_id)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Players WHERE Player_ID = %s", (player_id,))
    player = cursor.fetchone()

    if not player:
        return handle_error("Failed to retrieve the added player", 500)

    return jsonify({
        "player_ID": player[0], 
        "name": player[1], 
        "age": player[2], 
        "position": player[3], 
        "team_ID": player[4]
    }), 201

@app.route("/matches", methods=["POST"])
def add_match():
    data = request.get_json()
    match_id = data.get('match_ID')
    home_team_id = data.get('home_team_ID')
    away_team_id = data.get('away_team_ID')
    date = data.get('date')
    home_score = data.get('home_score')
    away_score = data.get('away_score')

    if not all([match_id, home_team_id, away_team_id, date, home_score, away_score]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Matches (Match_ID, Home_Team_ID, Away_Team_ID, Date, Home_Score, Away_Score) VALUES (%s, %s, %s, %s, %s, %s)",
        (match_id, home_team_id, away_team_id, date, home_score, away_score)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Matches WHERE Match_ID = %s", (match_id,))
    match = cursor.fetchone()

    if not match:
        return handle_error("Failed to retrieve the added match", 500)

    return jsonify({
        "match_ID": match[0], 
        "home_team_ID": match[1], 
        "away_team_ID": match[2], 
        "date": match[3], 
        "home_score": match[4], 
        "away_score": match[5]
    }), 201

@app.route("/leagues/<int:league_id>", methods=["DELETE"])
def delete_league(league_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Leagues WHERE League_ID = %s", (league_id,))
    mysql.connection.commit()

    if cursor.rowcount == 0:
        return handle_error("League not found", 404)

    return jsonify({"message": "League deleted successfully"}), 200

@app.route("/teams/<int:team_id>", methods=["DELETE"])
def delete_team(team_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Teams WHERE Team
