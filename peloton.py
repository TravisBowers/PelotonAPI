import requests
import json
from pandas import json_normalize
import os
import datetime
from matplotlib import pyplot as plt
import jmespath
import jinja2
import numpy as np

MAX_WORKOUTS = 2
METRICS_RESOLUTION = 100


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
    url = "https://api.onepeloton.com/api/user/{id}/workouts?status=COMPLETE?fitness_discipline=cycling&limit={max_workouts}&page=0".format(id = user_id, max_workouts = MAX_WORKOUTS)
    data = session.get(url).json()
    df_workouts_raw = json_normalize(data['data'])
    #print(json.dumps(data, indent=4))
    return df_workouts_raw

def get_workout_data(session, workout_id):
    url = 'https://api.onepeloton.com/api/workout/{}'.format(workout_id)
    response = session.get(url)
    data = response.json()
    url = 'https://api.onepeloton.com/api/workout/{id}/performance_graph?every_n={metrics_resolution}'.format(id=workout_id, metrics_resolution=METRICS_RESOLUTION)
    response = session.get(url)
    performance_graph = response.json()
    data.update(performance_graph)

    return data

def get_workout_data_list(s, workout_id_list):
    workout_data_list = []
    print("Gathering data for all completed rides")
    for i in workout_id_list:
        workout_id = i[0]
        print("getting data for workout id: "+ str(workout_id))
        workout_data_list.append(get_workout_data(s, workout_id))
    return workout_data_list

def generate_workout_page( workout_dict )
    
    # print(json.dumps(data, indent=4))
    # print(str(type(data)))
    context = {
        'metrics' :workout_dict['metrics'],
        'output_values': list(filter(lambda x:x['slug'] == "output", metrics))[0]['values'],
        'cadence_values': list(filter(lambda x:x['slug'] == "cadence", metrics))[0]['values'],
        'resistance_values': list(filter(lambda x:x['slug'] == "resistance", metrics))[0]['values'],
        'speed_values': list(filter(lambda x:x['slug'] == "speed", metrics))[0]['values'],
        heart_rate_values = list(filter(lambda x:x['slug'] == "heart_rate", metrics))[0]['values'],
        heart_rate_zones = list(filter(lambda x:x['slug'] == "heart_rate", metrics))[0]['zones'],
        created_at = workout_dict['created_at'],
        workout_date = datetime.datetime.fromtimestamp(created_at),
        workout_difficulty = workout_dict['ride']['difficulty_rating_avg'],
        workout_title = workout_dict['ride']['title'],
        workout_description = workout_dict['ride']['description'],
        workout_duration = workout_dict['ride']['duration'],
        workout_image_url = workout_dict['ride']['image_url'],
        instructor_id = workout_dict['ride']['instructor_id'],
        class_id = workout_dict['ride']['id'],
        class_url = "https://members.onepeloton.com/classes/cycling?modal=classDetailsModal&classId={}".format(class_id),
        ftp_info = workout_dict['ftp_info'],
        leaderboard_rank = workout_dict['leaderboard_rank'],
        total_leaderboard_users = workout_dict['total_leaderboard_users'],
    }
    #leaderboard_percentile = 1.0 - (float(leaderboard_rank)/float(total_leaderboard_users))

    environment= jinja2.Environment(loader=jinja2.FileSystemLoader("templates"))
    template = environment.get_template("workout_summary.j2")
    filename = "./workouts/{}.md".format(created_at)
    content = template.render()


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
    print("Gathering data for "+ str(len(workout_ids))+ " workouts")
    #quit()
    workout_dataset = get_workout_data_list(s,workout_ids)
    print(str(type(workout_dataset)))
    print("data for each workout is stored as type: "+ str(type(workout_dataset[0])))
    print(json.dumps(workout_dataset, indent=4))
    
    dates = jmespath.search('[*].created_at',workout_dataset)
    ftps = jmespath.search('[*].ftp_info.ftp',workout_dataset)
    
  



if __name__ == "__main__":
    main()
