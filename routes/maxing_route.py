import datetime

from flask import request, render_template, Blueprint, flash, redirect, session
from werkzeug.utils import secure_filename
import datetime
from datetime import datetime, timedelta, timezone
import os
import requests
import json
import wom
import copy
from wom import Skills, Skill
from utils import database

maxing_routes = Blueprint("maxing_routes", __name__)
lvl99xp = 13034431





@maxing_routes.route('/', methods=['GET'])
async def home():
    '''
    get cookies to see if username exists
    get cookie info for rates also
    fill with data from wom
    fill rates from cookie

    clear_session_data()
    session['RSN'] = 'taercy'
    session['start_time'] = datetime.now(timezone.utc) - timedelta(hours=2)
    '''

    await check_session_validity()

    return render_template('maxing_templates/maxing_home.html', currentXP=session['currentXP'],
                           currentLevel=session['currentLevel'],xpLeft=session['xpLeft'], gainedDay=session['gainedDay'], gainedMonth=session['gainedMonth'])


@maxing_routes.route('/road', methods=['GET'])
async def road():
    return render_template('maxing_templates/maxing_home.html')


async def check_session_validity():
    # if the session doesn't have a set start time, set one, set dummy data, and wait for user input
    if session.get('start_time') is None:
        session['start_time'] = datetime.now(timezone.utc)
        # session values will be null, set them to null or reasonable values
        make_dummy_session_data()
    # else a session start time exists
    else:
        time_difference = datetime.now(timezone.utc) - session.get('start_time')
        # if session hasn't refreshed in two hours, then refresh timer and data from stored username
        if time_difference > timedelta(hours=2):
            session['start_time'] = datetime.now(timezone.utc)

            if session.get('RSN') is None:
                make_dummy_session_data()
            else:
                # maybe validate name somehow with wom?
                # else call get data on username
                await get_data_from_rsn(session.get('RSN'))

        # else, the user has session data, and it's been less than an hour since it was refreshed
        # so session data should be up-to-date, either with an RSN and relevant data
        # or no RSN and base skills
        # users can still update the relevant data by submitting a new username with get_data_from_rsn


def clear_session_data():
    # set session details with new data
    session['RSN'] = None
    session['start_time'] = None

    session['currentLevel'] = None
    session['currentXP'] = None
    session['xpLeft'] = None
    session['gainedDay'] = None
    session['gainedMonth'] = None


async def get_data_from_rsn(rsn):

    # check rsn for validity so we dont make a bunch of calls for no reason

    #
    current_xp = {}
    current_level = {}
    xp_left = {}
    gained_day = {}
    gained_month = {}

    client = wom.Client(
        "o901h0ovbwg1t8q3w9jbybee",
        user_agent="@taercy",
    )
    await client.start()

    # result = await client.players.get_details("taercy")
    gains_day_result = await client.players.get_gains(session.get('RSN'), period=wom.Period.Day)
    gains_month_result = await client.players.get_gains(session.get('RSN'), period=wom.Period.Month)

    ''' 
    if result.is_ok:
        # The result is ok, so we can unwrap here
        details = result.unwrap()
        skills_details = getSkillsDetails(details)
        for skill in skills_details:
            xp_left[skill] = lvl99xp - skills_details[skill].experience
            if xp_left[skill] < 0:
                xp_left[skill] = "Done!"



    else:
        # Lets see what went wrong
        print(f"Error: {result.unwrap_err()}")

        # Close the client
    '''
    if gains_day_result.is_ok:
        details = gains_day_result.unwrap()
        gains_details = getGainedDetails(details)

        for skill in gains_details:
            current_xp[skill] = gains_details[skill].experience.end
            current_level[skill] = gains_details[skill].level.end
            xp_left[skill] = lvl99xp - current_xp[skill]
            if int(xp_left[skill]) < 0:
                xp_left[skill] = "Done!"
            gained_day[skill] = gains_details[skill].experience.gained
        session['currentLevel'] = current_level
        session['currentXP'] = current_xp
        session['xpLeft'] = xp_left
        session['gainedDay'] = gained_day



    else:
        # Lets see what went wrong
        print(f"Error: {gains_day_result.unwrap_err()}")

    if gains_month_result.is_ok:
        details = gains_month_result.unwrap()
        gains_details = getGainedDetails(details)

        for skill in gains_details:
            gained_month[skill] = gains_details[skill].experience.gained
        session['gainedMonth'] = gained_month

    else:
        # Lets see what went wrong
        print(f"Error: {gains_day_result.unwrap_err()}")

    # Close the client
    await client.close()




def make_dummy_session_data():
    '''

        We need to set up a bunch of data here on baby's first visit
        No RSN because it will be set later on button press, we just need the view to load with filler data
        We need to create a bunch of skill data that lines up with loading our view
        We need to create a bunch of expected xp / hr values

    '''
    # set up temp lists for manipulation of data
    current_xp = {}
    current_level = {}
    xp_left = {}
    gained_day = {}
    gained_month = {}
    skills_copy = [skill.name for skill in Skills]
    # overall and hitpoints are a little different from other skills at base level
    current_level["Overall"] = 32
    current_xp["Overall"] = 1154
    xp_left["Overall"] = 299790759
    gained_day["Overall"] = 0
    gained_month["Overall"] = 0

    current_level["Hitpoints"] = 10
    current_xp["Hitpoints"] = 1154
    xp_left["Hitpoints"] = 13033277
    gained_day["Hitpoints"] = 0
    gained_month["Hitpoints"] = 0

    skills_copy.remove("Overall")
    skills_copy.remove("Hitpoints")
    # every other skill gets set the same
    for skill in skills_copy:
            current_level[skill] = 1
            current_xp[skill] = 0
            xp_left[skill] = lvl99xp - current_xp[skill]
            gained_day[skill] = 0
            gained_month[skill] = 0

    # set session details with new data
    session['currentLevel'] = current_level
    session['currentXP'] = current_xp
    session['xpLeft'] = xp_left
    session['gainedDay'] = gained_day
    session['gainedMonth'] = gained_month

# might be useless haven't gotten to it yet
def getSkillsDetails(PlayerDetails):
    player = PlayerDetails.latest_snapshot.data.skills

    skills_dict = {}
    for skill in Skills:
        skills_dict[skill.name] = player[skill]

    return skills_dict



def getGainedDetails(gainsDetails):

    gains = gainsDetails.data.skills
    gained_dict = {}
    for skill in gains:
        gained_dict[skill.name] = gains[skill]

    return gained_dict



