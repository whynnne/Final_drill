import pytest
from app import app

@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_cursor

def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"WELCOME TO LEAGUES DATABASE" in response.data

def test_get_players_empty(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/players')
    assert response.status_code == 404
    assert b"No players found" in response.data

def test_get_players(mock_db):
    mock_db.fetchall.return_value = [(1, 'Player One', 'Forward', 'Team A')]
    client = app.test_client()
    response = client.get('/players')
    assert response.status_code == 200
    assert b"Player One" in response.data

def test_add_player_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/players', json={})
    assert response.status_code == 400
    assert b"Player ID is required" in response.data

def test_add_player_success(mock_db):
    client = app.test_client()
    mock_db.rowcount = 1
    response = client.post('/players', json={'player_ID': 1, 'name': 'Player One'})
    assert response.status_code == 201
    assert b"Player with ID 1 added successfully" in response.data

def test_update_player_missing_fields(mock_db):
    client = app.test_client()
    response = client.put('/players/1', json={})
    assert response.status_code == 400
    assert b"No updates provided for the player" in response.data

def test_update_player_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.put('/players/999', json={'name': 'Updated Name'})
    assert response.status_code == 404
    assert b"Player not found" in response.data

def test_delete_player_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.delete('/players/999')
    assert response.status_code == 404
    assert b"Player not found" in response.data

def test_delete_player_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.delete('/players/1')
    assert response.status_code == 200
    assert b"Player with ID 1 has been deleted." in response.data

def test_get_games_empty(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/games')
    assert response.status_code == 404
    assert b"No games found" in response.data

def test_get_games(mock_db):
    mock_db.fetchall.return_value = [(101, 'Game One', 'Soccer')]
    client = app.test_client()
    response = client.get('/games')
    assert response.status_code == 200
    assert b"Game One" in response.data

def test_add_game_success(mock_db):
    client = app.test_client()
    mock_db.rowcount = 1
    response = client.post('/games', json={'game_code': 101, 'name': 'Game One'})
    assert response.status_code == 201
    assert b"Game with code 101 added successfully" in response.data

def test_update_game_not_found(mock_db):
    mock_db.rowcount = 0
    client = app.test_client()
    response = client.put('/games/999', json={'name': 'Updated Game'})
    assert response.status_code == 404
    assert b"Game not found" in response.data

def test_delete_game_success(mock_db):
    mock_db.rowcount = 1
    client = app.test_client()
    response = client.delete('/games/101')
    assert response.status_code == 200
    assert b"Game with code 101 has been deleted." in response.data

if __name__ == "__main__":
    pytest.main()
