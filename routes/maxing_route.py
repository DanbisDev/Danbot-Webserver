from flask import request, render_template, Blueprint, flash, redirect
from werkzeug.utils import secure_filename
import os
import requests
import json
import wom
from wom import Skills, Skill
from utils import database

maxing_routes = Blueprint("maxing_routes", __name__)

@maxing_routes.route('/', methods=['GET'])
async def home():
    '''
    get cookies to see if username exists
    get cookie info for rates also
    fill with data from wom
    fill rates from cookie



    # Send a GET request to the API
    response = requests.get('https://jsonplaceholder.typicode.com/todos')

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()

        # Extract and print specific information
        print(data)
    else:
        print("Failed to retrieve data")
    '''
    client = wom.Client(
        "o901h0ovbwg1t8q3w9jbybee",
        user_agent="@taercy",
    )
    await client.start()
    skillsdetails = []
    '''
    result = await client.players.get_details("taercy")
    if result.is_ok:
        # The result is ok, so we can unwrap here
        details = result.unwrap()
        skillsdetails = getSkillsInfo(details)




    else:
        # Lets see what went wrong
        print(f"Error: {result.unwrap_err()}")

        # Close the client
    '''
    for skill in Skills:
        tempSkill = Skill()
        tempSkill.metric =
        tempSkill.experience = 1000000
        skillsdetails.append(skill.name, tempSkill )


    await client.close()
    return render_template('maxing_templates/maxing_home.html', skillsInfo = skillsdetails)


def getSkillsInfo(PlayerDetails):
    player = PlayerDetails.latest_snapshot.data.skills

    skills_dict = {}
    for skill in Skills:
        skills_dict[skill.name] = player[skill]

    return skills_dict

