from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "Leagues"
mysql = MySQL(app)

def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

@app.route("/")
def hello_world():
    return "WELCOME TO LEAGUES DATABASE"

@app.route("/players")
def get_players():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Players")
    players = cursor.fetchall()
    if not players:
        return handle_error("No players found", 404)
    
    players_list = [
        {
            "player_id": player[0], 
            "first_name": player[1],
            "last_name": player[2],
            "gender": player[3],
            "address": player[4]
        }
        for player in players
    ]
    
    return jsonify(players_list), 200

@app.route("/games")
def get_games():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Games")
    games = cursor.fetchall()
    if not games:
        return handle_error("No games found", 404)

    games_list = [
        {
            "game_code": game[0], 
            "game_name": game[1], 
            "game_description": game[2]
        }
        for game in games
    ]
    
    return jsonify(games_list), 200

@app.route("/teams")
def get_teams():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Teams")
    teams = cursor.fetchall()
    if not teams:
        return handle_error("No teams found", 404)

    teams_list = [
        {
            "team_id": team[0], 
            "team_name": team[1], 
            "created_by_player_id": team[2], 
            "date_created": team[3]
        }
        for team in teams
    ]
    
    return jsonify(teams_list), 200

@app.route("/matches")
def get_matches():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Matches")
    matches = cursor.fetchall()
    if not matches:
        return handle_error("No matches found", 404)

    matches_list = [
        {
            "match_id": match[0],
            "game_code": match[1], 
            "team_1_id": match[2], 
            "team_2_id": match[3], 
            "match_date": match[4], 
            "result": match[5]
        }
        for match in matches
    ]
    
    return jsonify(matches_list), 200

@app.route("/players", methods=["POST"])
def add_player():
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    gender = data.get('gender')
    address = data.get('address')

    if not all([first_name, last_name, gender, address]):
        return handle_error("Missing required fields", 400)
    
    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Players (first_name, last_name, gender, address) VALUES (%s, %s, %s, %s)",
        (first_name, last_name, gender, address)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Players WHERE player_id = LAST_INSERT_ID()")
    player = cursor.fetchone()

    if not player:
        return handle_error("Failed to retrieve the added player", 500)

    return jsonify({
        "player_id": player[0], 
        "first_name": player[1],
        "last_name": player[2],
        "gender": player[3],
        "address": player[4]
    }), 201

@app.route("/games", methods=["POST"])
def add_game():
    data = request.get_json()
    game_name = data.get('game_name')
    game_description = data.get('game_description')

    if not game_name:
        return handle_error("Game name is required", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Games (game_name, game_description) VALUES (%s, %s)", 
        (game_name, game_description)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Games WHERE game_code = LAST_INSERT_ID()")
    game = cursor.fetchone()

    if not game:
        return handle_error("Failed to retrieve the added game", 500)

    return jsonify({
        "game_code": game[0], 
        "game_name": game[1], 
        "game_description": game[2]
    }), 201

@app.route("/teams", methods=["POST"])
def add_team():
    data = request.get_json()
    team_name = data.get('team_name')
    created_by_player_id = data.get('created_by_player_id')
    date_created = data.get('date_created')

    if not all([team_name, created_by_player_id, date_created]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Teams (team_name, created_by_player_id, date_created) VALUES (%s, %s, %s)",
        (team_name, created_by_player_id, date_created)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Teams WHERE team_id = LAST_INSERT_ID()")
    team = cursor.fetchone()

    if not team:
        return handle_error("Failed to retrieve the added team", 500)

    return jsonify({
        "team_id": team[0], 
        "team_name": team[1], 
        "created_by_player_id": team[2], 
        "date_created": team[3]
    }), 201

@app.route("/matches", methods=["POST"])
def add_match():
    data = request.get_json()
    game_code = data.get('game_code')
    team_1_id = data.get('team_1_id')
    team_2_id = data.get('team_2_id')
    match_date = data.get('match_date')
    result = data.get('result')

    if not all([game_code, team_1_id, team_2_id, match_date]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Matches (game_code, team_1_id, team_2_id, match_date, result) VALUES (%s, %s, %s, %s, %s)",
        (game_code, team_1_id, team_2_id, match_date, result)
    )
    mysql.connection.commit()

    cursor.execute("SELECT * FROM Matches WHERE match_id = LAST_INSERT_ID()")
    match = cursor.fetchone()

    if not match:
        return handle_error("Failed to retrieve the added match", 500)

    return jsonify({
        "match_id": match[0],
        "game_code": match[1], 
        "team_1_id": match[2], 
        "team_2_id": match[3], 
        "match_date": match[4], 
        "result": match[5]
    }), 201

if __name__ == "__main__":
    app.run(debug=True)
