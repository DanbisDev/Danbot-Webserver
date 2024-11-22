import os
import urllib
from collections import defaultdict

import discord
from discord.ext import commands

from utils import bingo, database, db_entities
from utils.autocomplete import player_names, team_names, tile_names, fuzzy_autocomplete, wrapup_player_names, \
    wrapup_boss_names

ftext = "\u001b["

fnormal = "0;"
fbolt = "1;"
funderline = "4;"

fred = "31m"
fgreen = "32m"
fyellow = "33m"
fblue = "34m"
fwhite = "37m"
fend = ftext + "0m"

import os

def setup_names():
    folder_path = 'static/images/setups'
    folder_names = []

    for item_name in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item_name)
        if os.path.isdir(item_path):
            folder_names.append(item_name)

    return folder_names



class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="help", description="A list of all my cool commands!")
    async def help(self, ctx: discord.ApplicationContext):
        commands_info = {
            "help": "A list of all my cool commands!",
            "dink": "Use this command to get help setting up your dink plugin.",
            "player": "Get a bunch of data about a player in the bingo.",
            "team": "Get a bunch of data about a team in the bingo.",
            "leaderboard": "Show the current standings amongst teams and players.",
            "add_split": "Add split to your account!",
            "get_splits": "Shows how much gold you have split on your account!",
            "pb": "Shows the current personal (clan) best time for a given boss"
        }

        response = "**Here are all my available commands:**\n\n"
        for command, description in commands_info.items():
            response += f"/{command} - {description}\n"

        await ctx.respond(response)

    @discord.slash_command(name="dink", description="Use this command to get help setting up your dink plugin")
    async def dink(self, ctx:discord.ApplicationContext):
        await ctx.defer()
        server_ip = os.getenv('SERVER_IP')
        player_url = f"http://{server_ip}/tutorial/dink"
        await ctx.respond(player_url)

    @discord.slash_command(name="player", description="Get a bunch of data about a player in the bingo")
    async def player(self, ctx: discord.ApplicationContext,
                     player_name: discord.Option(str, "What is the username?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, player_names()))):
        await ctx.defer()
        server_ip = os.getenv('SERVER_IP')
        player_url = f"http://{server_ip}/user/player/{player_name.replace(' ', '%20')}"
        await ctx.respond(player_url)

    @discord.slash_command(name="add_split", description="Add split to your account!")
    async def add_split(self, ctx: discord.ApplicationContext,
                        player_name: discord.Option(str, "What is your username?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, wrapup_player_names())),
                        amount_split: discord.Option(int, "How much gold did you split?")):
        await ctx.defer()
        database.add_wrapup_player_split(player_name, amount_split)
        await ctx.respond(f"Successfully added {amount_split} to {player_name}!")

    @discord.slash_command(name="get_splits", description="Shows how much gold you have split on your account!")
    async def get_split(self, ctx: discord.ApplicationContext,
                        player_name: discord.Option(str, "What is your username?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, wrapup_player_names()))):
        await ctx.defer()
        player_splits = database.get_wrapup_player_split(player_name)
        await ctx.respond(f"You have split {player_splits} gold!")

    import discord
    import datetime

    @discord.slash_command(name="pb", description="Get the clan's current personal best")
    async def pb(self, ctx: discord.ApplicationContext,
                 boss_name: discord.Option(str, "What is the bossname?",
                                           autocomplete=lambda ctx: fuzzy_autocomplete(ctx, wrapup_boss_names()))):
        await ctx.defer()

        # Retrieve the personal best (pb) and players from the database
        pb, players = database.get_wrapup_personal_best(boss_name)

        if pb is None:
            await ctx.respond(f"There is no personal best found for {boss_name}...")

        # Convert total seconds (pb) into a readable format
        def format_time(seconds):
            # Calculate hours, minutes, and seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60

            # Build the time string
            time_str = []
            if hours > 0:
                time_str.append(f"{hours} hour{'s' if hours > 1 else ''}")
            if minutes > 0:
                time_str.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
            if seconds > 0 or len(time_str) == 0:  # Always show seconds if there's no hours or minutes
                time_str.append(f"{seconds} second{'s' if seconds != 1 else ''}")

            # Join and return the formatted string
            return ", ".join(time_str)

        # Format the personal best time
        formatted_pb = format_time(pb)

        # Respond with the formatted personal best time and the players
        await ctx.respond(f"The Fatalis personal best for {boss_name} is {formatted_pb} gotten by {players}")

    @discord.slash_command(name="team", description="Get a bunch of data about a team in the bingo")
    async def team(self, ctx: discord.ApplicationContext,
                   team_name: discord.Option(str, "What is the team name?", autocomplete=lambda ctx: fuzzy_autocomplete(ctx, team_names()))):
        await ctx.defer()
        server_ip = os.getenv('SERVER_IP')
        team_url = f"http://{server_ip}/user/team/{team_name.replace(' ', '%20')}"
        await ctx.respond(team_url)


    @discord.slash_command(name="gear", description="View our catalog of gear setups for any content and budget")
    async def gear(self, ctx: discord.ApplicationContext,
                   setup: discord.Option(str, "What setup are you looking for?",
                                         autocomplete=lambda ctx: fuzzy_autocomplete(ctx, setup_names())),
                   budget: discord.Option(str, "Max or budget gear?",
                                          autocomplete=lambda ctx: fuzzy_autocomplete(ctx, ["budget", "max"]), default=None)):
        await ctx.defer()
        if budget is None:
            await ctx.respond(f""
                              f"# {setup.upper()}\n"
                              f"### BUDGET {setup.upper()}\n"
                              f"https://danbot.up.railway.app/static/images/setups/{setup}/budget.png\n"
                              f"### MAX {setup.upper()}\n"
                              f"https://danbot.up.railway.app/static/images/setups/{setup}/max.png\n")
        elif budget.lower() == "max":
            await ctx.respond(f"# MAX {setup.upper()}\n"
                              f"https://danbot.up.railway.app/static/images/setups/{setup}/max.png\n")
        elif budget.lower() == "budget":
            await ctx.respond(f"# BUDGET {setup.upper()}\n"
                              f"https://danbot.up.railway.app/static/images/setups/{setup}/budget.png\n")
        return



    @discord.slash_command(name="leaderboard", description="Show the current standings amongst teams and players")
    async def leaderboard(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        server_ip = os.getenv('SERVER_IP')
        leaderboard_url = f"http://{server_ip}/user/leaderboard"
        await ctx.respond(leaderboard_url)