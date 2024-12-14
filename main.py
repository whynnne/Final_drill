from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
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

if __name__ == '__main__':
    app.run(debug=True)
