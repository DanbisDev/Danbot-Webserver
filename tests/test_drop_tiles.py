import os
import sys

import pytest

import db_entities
from routes import drop_submit_route

sys.path.insert(0, os.path.abspath('..'))
import database
from main import app, create_app
from utils import spoof_drop


@pytest.fixture()
def app():
    app = create_app()
    # other setup can go here
    database.reset_tables()
    yield app
    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()

def test_relevant_drop_occurred(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_1.csv')


    json_data = spoof_drop.item_spoof_json("Danbis", "Coin pouch", 1)
    result = drop_submit_route.parse_loot(json_data, None)
    assert len(database.get_drops_by_item_name_and_team_id("Coin pouch", 1)) > 0
    assert result == True

def test_tile_completed(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_1.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Coin pouch", 1)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1
    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 1

def test_complex_trigger_weights(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_1.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Coins", 6)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 12/20

def test_multiple_completions(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_1.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Coins", 10)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 1
    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

    json_data = spoof_drop.item_spoof_json("Danbis", "Coins", 11)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 42/20
    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 2

    json_data = spoof_drop.item_spoof_json("Danbis", "Bones", 1)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player.tiles_completed == 62/20
    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 3

def test_drops_shared_by_team(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_1.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Coins", 5)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    json_data = spoof_drop.item_spoof_json("Deidera", "Coins", 5)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
    player_deidera = db_entities.Player(database.get_player_by_name("Deidera"))
    assert player_danbis.tiles_completed == 0.5
    assert player_deidera.tiles_completed == 0.5
    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

def test_collections(client):
    database.reset_tables()
    database.read_teams('tests/test_csvs/default_team_1.csv')
    database.read_tiles('tests/test_csvs/default_tiles_1.csv')

    json_data = spoof_drop.item_spoof_json("Danbis", "Air Rune", 1)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player_danbis.tiles_completed == 1/3

    json_data = spoof_drop.item_spoof_json("Deidera", "Iron bolts", 1)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player_deidera = db_entities.Player(database.get_player_by_name("Deidera"))
    assert player_deidera.tiles_completed == 1/3

    json_data = spoof_drop.item_spoof_json("Danbis", "Bronze arrow", 1)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player_danbis.tiles_completed == 2/3

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1

    json_data = spoof_drop.item_spoof_json("Danbis", "Earth rune", 1)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player_danbis = db_entities.Player(database.get_player_by_name("Danbis"))
    assert player_danbis.tiles_completed == 1

    json_data = spoof_drop.item_spoof_json("Deidera", "Fire rune", 1)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player_deidera = db_entities.Player(database.get_player_by_name("Deidera"))
    assert player_deidera.tiles_completed == 2/3

    json_data = spoof_drop.item_spoof_json("Deidera", "Steel arrow", 1)
    result = drop_submit_route.parse_loot(json_data, None)
    assert result == True

    player_deidera = db_entities.Player(database.get_player_by_name("Deidera"))
    assert player_deidera.tiles_completed == 1

    team = db_entities.Team(database.get_team_by_id(1))
    assert team.team_points == 1