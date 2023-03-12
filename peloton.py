import requests
import json
from pandas import json_normalize
import os
import datetime
from matplotlib import pyplot as plt

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
    url = "https://api.onepeloton.com/api/user/{id}/workouts?status=COMPLETE?fitness_discipline=cycling&limit=10000&page=0".format(id = user_id)
    data = session.get(url).json()
    df_workouts_raw = json_normalize(data['data'])
    #print(json.dumps(data, indent=4))
    return df_workouts_raw

def get_workout_data(session, workout_id):
    url = 'https://api.onepeloton.com/api/workout/{}'.format(workout_id)
    response = session.get(url)
    data = response.json()
    #print(json.dumps(data, indent=4))

    #extract useful values
    workout_dict={}
    
    
    created_at = data['created_at']
    workout_dict['workout_date'] = datetime.datetime.fromtimestamp(created_at)
    workout_dict['difficulty'] = data['ride']['difficulty_rating_avg']
    workout_dict['title'] = data['ride']['title']
    workout_dict['description'] = data['ride']['description']
    workout_dict['duration'] = data['ride']['duration']
    workout_dict['image_url'] = data['ride']['image_url']
    instructor_id = data['ride']['instructor_id']
    class_id = data['ride']['id']
    class_url = "https://members.onepeloton.com/classes/cycling?modal=classDetailsModal&classId={}".format(class_id)
    ftp_info = data['ftp_info']
    leaderboard_rank = data['leaderboard_rank']
    total_leaderboard_users = data['total_leaderboard_users']
    #leaderboard_percentile = 1.0 - (float(leaderboard_rank)/float(total_leaderboard_users))

    # get performance data
    url = 'https://api.onepeloton.com/api/workout/{}/performance_graph?every_n=500'.format(workout_id)
    response = session.get(url)
    performance_graph = response.json()
    data.update(performance_graph)

     
    
    # print(json.dumps(data, indent=4))
    # print(str(type(data)))
    metrics = performance_graph['metrics']
    output_values = list(filter(lambda x:x['slug'] == "output", metrics))[0]['values']
    cadence_values = list(filter(lambda x:x['slug'] == "cadence", metrics))[0]['values']
    resistance_values = list(filter(lambda x:x['slug'] == "resistance", metrics))[0]['values']
    speed_values = list(filter(lambda x:x['slug'] == "speed", metrics))[0]['values']
    heart_rate_values = list(filter(lambda x:x['slug'] == "heart_rate", metrics))[0]['values']
    heart_rate_zones = list(filter(lambda x:x['slug'] == "heart_rate", metrics))[0]['zones']
    # plt.plot(np.array(heart_rate_values), '.')
    # plt.show()
    # print(workout_date)
    # input(' press enter to continue')
    return data

def get_workout_data_list(s, workout_id_list):
    workout_data_list = []
    print("Gathering data for all completed rides")
    for i in workout_id_list:
        workout_id = i[0]
        print("getting data for workout id: "+ str(workout_id))
        workout_data_list.append(get_workout_data(s, workout_id))
    return workout_data_list


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
    quit()
    workout_dataset = get_workout_data_list(s,workout_ids)
    print(str(type(workout_dataset)))
    print("data for each workout is stored as type: "+ str(type(workout_dataset[0])))





if __name__ == "__main__":
    main()
