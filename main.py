import json
import datetime
import jwt
from flask import Flask, request, jsonify, abort
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "leagues"
app.config["SECRET_KEY"] = "liganiwynne"

mysql = MySQL(app)
bcrypt = Bcrypt(app)

def handle_error(error_msg, status_code):
    return jsonify({"error": error_msg}), status_code

@app.route("/")
def welcome():
    return """     <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gaming Leagues</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f9;
                color: #333;
                margin: 0;
                padding: 0;
                text-align: center;
                padding-top: 50px;
            }
            button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 1.2em;
                margin: 10px;
                cursor: pointer;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #2980b9;
            }
        </style>
    </head>
    <body>
        <button onclick="window.location.href='/players'">Players</button>
        <button onclick="window.location.href='/teams'">Teams</button>
        <button onclick="window.location.href='/games'">Games</button>
        <button onclick="window.location.href='/matches'">Matches</button>
    </body>
    </html>

    """

def validate_token():
    token = request.headers.get("x-access-token")
    if not token:
        return None, handle_error("Token is missing!", 401)
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        current_user = {"user_id": data["user_id"], "role": data["role"]}
        return current_user, None
    except Exception:
        return None, handle_error("Token is invalid!", 401)

def validate_role(current_user, valid_roles):
    if isinstance(valid_roles, str):
        valid_roles = [valid_roles]
    
    if current_user["role"] not in valid_roles:
        return jsonify({"error": "Unauthorized access"}), 403
    return None

users_data = {
    "users": []
}

def save_to_json():
    with open("users.json", "w") as f:
        json.dump(users_data, f)

def load_from_json():
    global users_data
    try:
        with open("users.json", "r") as f:
            users_data = json.load(f)
    except FileNotFoundError:
        save_to_json()

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password") or not data.get("role"):
        return handle_error("Missing required fields: username, password, and role are mandatory", 400)
    
    username = data["username"]
    password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    role = data["role"]

    load_from_json()
    for user in users_data["users"]:
        if user["username"] == username:
            return handle_error("Username already exists", 400)

    new_user = {"username": username, "password": password, "role": role}
    users_data["users"].append(new_user)
    save_to_json()

    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return handle_error("Missing required fields: username and password are mandatory", 400)
    
    username = data["username"]
    password = data["password"]
    
    load_from_json()
    for user in users_data["users"]:
        if user["username"] == username and bcrypt.check_password_hash(user["password"], password):
            token = jwt.encode(
                {
                    "user_id": username,
                    "role": user["role"],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                },
                app.config["SECRET_KEY"],
                algorithm="HS256",
            )
            return jsonify({"token": token}), 200
    return handle_error("Invalid credentials", 401)

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
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

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
    teams_list = [{"team_id": team[0], "team_name": team[1]} for team in teams]
    return jsonify(teams_list), 200

@app.route("/teams", methods=["POST"])
def add_team():
    current_user, error = validate_token()
    if error:
        return error

    data = request.get_json()
    team_name = data.get('team_name')

    if not team_name:
        return handle_error("Missing required field", 400)

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO Teams (team_name) VALUES (%s)", (team_name,))
    mysql.connection.commit()
    return jsonify({"message": "Team added successfully"}), 201

@app.route("/teams/<int:team_id>", methods=["PUT"])
def update_team(team_id):
    current_user, error = validate_token()
    if error:
        return error

    data = request.get_json()
    team_name = data.get('team_name')

    if not team_name:
        return handle_error("No updates provided", 400)

    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE Teams SET team_name = %s WHERE team_id = %s", (team_name, team_id))
    mysql.connection.commit()
    return jsonify({"message": "Team updated successfully"}), 200

@app.route("/teams/<int:team_id>", methods=["DELETE"])
def delete_team(team_id):
    current_user, error = validate_token()
    if error:
        return error

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Teams WHERE team_id = %s", (team_id,))
    mysql.connection.commit()
    return jsonify({"message": f"Team with ID {team_id} deleted"}), 200

# CRUD for Matches Table
@app.route("/matches", methods=["POST"])
def add_match():
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

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
    current_user, error = validate_token()
    if error:
        return error

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM Matches WHERE match_id = %s", (match_id,))
    mysql.connection.commit()
    return jsonify({"message": f"Match with ID {match_id} deleted"}), 200


if __name__ == "__main__":
    app.run(debug=True)
