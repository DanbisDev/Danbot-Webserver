from flask import render_template, Blueprint
from utils import scapify, database, db_entities, autocomplete
wrapup_routes = Blueprint("wrapup_routes", __name__)

@wrapup_routes.route("/player/<player_name>")
def player_page(player_name):
    try:
        wrapup_player = database.get_wrapup_player(player_name)
        wrapup_player = db_entities.WrapupPlayer(wrapup_player)
        wrapup_player.gold_gained = scapify.int_to_gp(wrapup_player.gold_gained)
        wrapup_player.gold_split = scapify.int_to_gp(wrapup_player.gold_split)
    except:
        wrapup_player = db_entities.WrapupPlayer()

    return render_template('wrapup_templates/player.html', wrapup_player=wrapup_player, playernames=autocomplete.wrapup_player_names())
