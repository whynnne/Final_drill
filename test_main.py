import pytest
from app import app

@pytest.fixture
def mock_db(mocker):
    mock_conn = mocker.patch('flask_mysqldb.MySQL.connection')
    mock_cursor = mocker.MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None
    mock_cursor.rowcount = 1
    
    return mock_cursor

def test_index():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b"WELCOME TO THE LEAGUES DATABASE" in response.data

def test_get_players_empty(mock_db):
    mock_db.fetchall.return_value = []
    client = app.test_client()
    response = client.get('/players')

    assert response.status_code == 404
    assert b"No players found" in response.data

def test_get_players(mock_db):
    mock_db.fetchall.return_value = [(1, 'Lionel Messi', 35, 'Forward'), (2, 'Cristiano Ronaldo', 37, 'Forward')]

    client = app.test_client()
    response = client.get('/players')

    assert response.status_code == 200
    assert b"Lionel Messi" in response.data
    assert b"Cristiano Ronaldo" in response.data

def test_add_player_missing_fields(mock_db):
    client = app.test_client()
    response = client.post('/players', json={})

    assert response.status_code == 400
    assert b"Player ID and name are required" in response.data

def test_add_player_success(mock_db):
    mock_db.rowcount = 1
    mock_db.fetchone.return_value = (1, 'Lionel Messi')

    client = app.test_client()
    response = client.post('/players', json={'player_ID': 1, 'name': 'Lionel Messi', 'age': 35, 'position': 'Forward'})

    assert response.status_code == 201
    assert b"player_ID" in response.data
    assert b"1" in response.data
    assert b"Lionel Messi" in response.data
    

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
    mock_db.fetchone.return_value = (1, 'Lionel Messi')
    mock_db.rowcount = 1

    client = app.test_client()
    response = client.delete('/players/1')

    assert response.status_code == 200
    assert b"Player with ID 1 has been deleted." in response.data
