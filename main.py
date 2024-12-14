from flask import Flask, request, jsonify
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
def welcome():
    return "Welcome to the Leagues Database API!"


# CRUD for Players Table
@app.route("/players", methods=["GET"])
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
    return jsonify({"message": "Player added successfully"}), 201

@app.route("/players/<int:player_id>", methods=["PUT"])
def update_player(player_id):
    data = request.get_json()
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    gender = data.get('gender')
    address = data.get('address')

    if not any([first_name, last_name, gender, address]):
        return handle_error("No updates provided", 400)

    updates = []
    values = []
    if first_name:
        updates.append("first_name = %s")
        values.append(first_name)
    if last_name:
        updates.append("last_name = %s")
        values.append(last_name)
    if gender:
        updates.append("gender = %s")
        values.append(gender)
    if address:
        updates.append("address = %s")
        values.append(address)
    values.append(player_id)

    query = f"UPDATE Players SET {', '.join(updates)} WHERE player_id = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(query, tuple(values))
    mysql.connection.commit()
    return jsonify({"message": "Player updated successfully"}), 200

@app.route("/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Players WHERE player_id = %s", (player_id,))
    mysql.connection.commit()
    return jsonify({"message": f"Player with ID {player_id} deleted"}), 200


# CRUD for Games Table
@app.route("/games", methods=["GET"])
def get_games():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Games")
    games = cursor.fetchall()
    if not games:
        return handle_error("No games found", 404)
    games_list = [{"game_code": game[0], "game_name": game[1], "game_description": game[2]} for game in games]
    return jsonify(games_list), 200

@app.route("/games", methods=["POST"])
def add_game():
    data = request.get_json()
    game_name = data.get('game_name')
    game_description = data.get('game_description')

    if not all([game_name, game_description]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Games (game_name, game_description) VALUES (%s, %s)",
        (game_name, game_description)
    )
    mysql.connection.commit()
    return jsonify({"message": "Game added successfully"}), 201

@app.route("/games/<int:game_code>", methods=["PUT"])
def update_game(game_code):
    data = request.get_json()
    game_name = data.get('game_name')
    game_description = data.get('game_description')

    if not any([game_name, game_description]):
        return handle_error("No updates provided", 400)

    updates = []
    values = []
    if game_name:
        updates.append("game_name = %s")
        values.append(game_name)
    if game_description:
        updates.append("game_description = %s")
        values.append(game_description)
    values.append(game_code)

    query = f"UPDATE Games SET {', '.join(updates)} WHERE game_code = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(query, tuple(values))
    mysql.connection.commit()
    return jsonify({"message": "Game updated successfully"}), 200

@app.route("/games/<int:game_code>", methods=["DELETE"])
def delete_game(game_code):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Games WHERE game_code = %s", (game_code,))
    mysql.connection.commit()
    return jsonify({"message": f"Game with Code {game_code} deleted"}), 200


# CRUD for Teams Table
@app.route("/teams", methods=["GET"])
def get_teams():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM Teams")
    teams = cursor.fetchall()
    if not teams:
        return handle_error("No teams found", 404)
    teams_list = [
        {"team_id": team[0], "team_name": team[1], "created_by_player_id": team[2], "date_created": team[3]}
        for team in teams
    ]
    return jsonify(teams_list), 200

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
    return jsonify({"message": "Team added successfully"}), 201

@app.route("/teams/<int:team_id>", methods=["PUT"])
def update_team(team_id):
    data = request.get_json()
    team_name = data.get('team_name')
    created_by_player_id = data.get('created_by_player_id')
    date_created = data.get('date_created')

    if not any([team_name, created_by_player_id, date_created]):
        return handle_error("No updates provided", 400)

    updates = []
    values = []
    if team_name:
        updates.append("team_name = %s")
        values.append(team_name)
    if created_by_player_id:
        updates.append("created_by_player_id = %s")
        values.append(created_by_player_id)
    if date_created:
        updates.append("date_created = %s")
        values.append(date_created)
    values.append(team_id)

    query = f"UPDATE Teams SET {', '.join(updates)} WHERE team_id = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(query, tuple(values))
    mysql.connection.commit()
    return jsonify({"message": "Team updated successfully"}), 200

@app.route("/teams/<int:team_id>", methods=["DELETE"])
def delete_team(team_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Teams WHERE team_id = %s", (team_id,))
    mysql.connection.commit()
    return jsonify({"message": f"Team with ID {team_id} deleted"}), 200


# CRUD for Matches Table
@app.route("/matches", methods=["GET"])
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

@app.route("/matches", methods=["POST"])
def add_match():
    data = request.get_json()
    game_code = data.get('game_code')
    team_1_id = data.get('team_1_id')
    team_2_id = data.get('team_2_id')
    match_date = data.get('match_date')
    result = data.get('result')

    if not all([game_code, team_1_id, team_2_id, match_date, result]):
        return handle_error("Missing required fields", 400)

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO Matches (game_code, team_1_id, team_2_id, match_date, result) VALUES (%s, %s, %s, %s, %s)",
        (game_code, team_1_id, team_2_id, match_date, result)
    )
    mysql.connection.commit()
    return jsonify({"message": "Match added successfully"}), 201

@app.route("/matches/<int:match_id>", methods=["PUT"])
def update_match(match_id):
    data = request.get_json()
    game_code = data.get('game_code')
    team_1_id = data.get('team_1_id')
    team_2_id = data.get('team_2_id')
    match_date = data.get('match_date')
    result = data.get('result')

    if not any([game_code, team_1_id, team_2_id, match_date, result]):
        return handle_error("No updates provided", 400)

    updates = []
    values = []
    if game_code:
        updates.append("game_code = %s")
        values.append(game_code)
    if team_1_id:
        updates.append("team_1_id = %s")
        values.append(team_1_id)
    if team_2_id:
        updates.append("team_2_id = %s")
        values.append(team_2_id)
    if match_date:
        updates.append("match_date = %s")
        values.append(match_date)
    if result:
        updates.append("result = %s")
        values.append(result)
    values.append(match_id)

    query = f"UPDATE Matches SET {', '.join(updates)} WHERE match_id = %s"
    cursor = mysql.connection.cursor()
    cursor.execute(query, tuple(values))
    mysql.connection.commit()
    return jsonify({"message": "Match updated successfully"}), 200

@app.route("/matches/<int:match_id>", methods=["DELETE"])
def delete_match(match_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Matches WHERE match_id = %s", (match_id,))
    mysql.connection.commit()
    return jsonify({"message": f"Match with ID {match_id} deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True)
