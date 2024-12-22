from flask import render_template, Blueprint
from utils import scapify, database, db_entities, autocomplete
wrapup_routes = Blueprint("wrapup_routes", __name__)

@wrapup_routes.route("/player/<player_name>")
def player_page(player_name):
    try:
        wrapup_player = database.get_wrapup_player(player_name)
        wrapup_player = db_entities.WrapupPlayer(wrapup_player)
    except:
        wrapup_player = db_entities.WrapupPlayer()

    return render_template('wrapup_templates/player.html', wrapup_player=wrapup_player, player_names=autocomplete.player_names())
