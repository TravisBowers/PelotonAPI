import pandas as pd
import requests
import json
from pandas import json_normalize
from functools import reduce
import os
import openpyxl
import datetime
import matplotlib.pyplot as plt

import numpy as np

def peloton_login( user, pw, session):
    payload = {'username_or_email': user, 'password':pw}
    session.post('https://api.onepeloton.com/auth/login', json=payload)

def get_user_id(session):

    me_url = 'https://api.onepeloton.com/api/me'
    response = session.get(me_url)
    apidata = session.get(me_url).json()
    my_id = (apidata['id'])
    return my_id

def get_completed_rides(session, user_id):
    url = "https://api.onepeloton.com/api/user/{id}/workouts?status=COMPLETE?fitness_discipline=cycling".format(id = user_id)
    data = session.get(url).json()
    df_workouts_raw = json_normalize(data['data'])
    #print(json.dumps(data, indent=4))
    return df_workouts_raw

def get_workout_metrics(session, workout_id):
    url = 'https://api.onepeloton.com/api/workout/{}'.format(workout_id)
    response = session.get(url)
    data = response.json()
    print(json.dumps(data, indent=4))

    #extract useful values
    created_at = data['created_at']
    workout_date = datetime.datetime.fromtimestamp(created_at)
    difficulty = data['ride']['difficulty_rating_avg']
    title = data['ride']['title']
    description = data['ride']['description']
    duration = data['ride']['duration']
    image_url = data['ride']['image_url']
    instructor_id = data['ride']['instructor_id']
    class_id = data['ride']['id']
    class_url = "https://members.onepeloton.com/classes/cycling?modal=classDetailsModal&classId={}".format(class_id)
    ftp_info = data['ftp_info']
    leaderboard_rank = data['leaderboard_rank']
    total_leaderboard_users = data['total_leaderboard_users']
    leaderboard_percentile = 1.0 - (float(leaderboard_rank)/float(total_leaderboard_users))

    # get performance data
    url = 'https://api.onepeloton.com/api/workout/{}/performance_graph?every_n=1'.format(workout_id)
    response = session.get(url)
    data = response.json()
    metrics = data['metrics']
    #print(json.dumps(metrics, indent=4))
    output_values = list(filter(lambda x:x['slug'] == "output", metrics))[0]['values']
    cadence_values = list(filter(lambda x:x['slug'] == "cadence", metrics))[0]['values']
    resistance_values = list(filter(lambda x:x['slug'] == "resistance", metrics))[0]['values']
    speed_values = list(filter(lambda x:x['slug'] == "speed", metrics))[0]['values']
    heart_rate_values = list(filter(lambda x:x['slug'] == "heart_rate", metrics))[0]['values']

    plt.plot(np.array(heart_rate_values), '.')
    plt.show()
    print(workout_date)
    input(' press enter to continue')
    quit()
    df_workout_metrics = json_normalize(data['metrics'])
    return df_workout_metrics


def main():
    user = os.getenv('PELOTON_USER')
    pw = os.getenv('PELOTON_PASSWORD')
    excel = './peloton.xlsx'
    s = requests.Session()
    peloton_login(user, pw, s)
    user_id = get_user_id(s)
    workouts = get_completed_rides(s, user_id)
    df_workout_ids = workouts.filter(['id'], axis=1)
    workout_ids = df_workout_ids.values.tolist()

    for i in workout_ids:
        workout_id = i[0]
        metrics = get_workout_metrics(s, workout_id)
        #print(metrics.to_string())

    #print(workout_ids)



if __name__ == "__main__":
    main()
