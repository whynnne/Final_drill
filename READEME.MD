```

## Configuration
To configure the database:
1. Upload the ```Leagues``` MySQL database to your server or local machine.
2. Update the database configuration in the Flask app with your database connection details.

Environment variables needed:
- ```MYSQL_HOST```: The host for the MySQL database (e.g., localhost or IP address of the database server)
- ```MYSQL_USER```: MySQL username (e.g., root)
- ```MYSQL_PASSWORD```: MySQL password
- ```MYSQL_DB```: Name of the database (e.g., Leagues)

## API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| / | GET | Welcome message |
| /players | GET | List all players |
| /players | POST | Add a new player |
| /players/<player_id> | PUT | Update a player's details |
| /players/<player_id> | DELETE | Delete a player |
| /games | GET | List all games |
| /games | POST | Add a new game |
| /games/<game_code> | PUT | Update a game's details |
| /games/<game_code> | DELETE | Delete a game |
| /teams | GET | List all teams |
| /teams | POST | Add a new team |
| /teams/<team_id> | PUT | Update a team's details |
| /teams/<team_id> | DELETE | Delete a team |
| /matches | GET | List all matches |
| /matches | POST | Add a new match |
| /matches/<match_id> | PUT | Update a match's details |
| /matches/<match_id> | DELETE | Delete a match |

## Git Commit Guidelines
Use conventional commits:
```bash
feat: add team management feature
fix: resolve database connection issue
docs: update API documentation
test: add match validation tests
```
