import pandas as pd
import requests
import json
from pandas import json_normalize
from functools import reduce
import os
import openpyxl

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
    return df_workouts_raw



def main():
    user = os.getenv('PELOTON_USER')
    pw = os.getenv('PELOTON_PASSWORD')
    excel = './peloton.xlsx'
    s = requests.Session()
    peloton_login(user, pw, s)
    user_id = get_user_id(s)
    workouts = get_completed_rides(s, user_id)

    print(workouts.to_string())



if __name__ == "__main__":
    main()
