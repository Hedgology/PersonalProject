from sqlite3 import ProgrammingError
from webbrowser import get
from sqlalchemy import create_engine
import urllib.request
import requests
import json
import pandas as pd
import pickle
from datetime import datetime
import os
from selenium import webdriver
import MySQLdb

PATH = 'C:\Program Files (x86)\chromedriver.exe'


######################
# Creating Engine
######################

engine = create_engine("mysql+mysqldb://root:root@localhost/Warzone")
my_conn = engine.connect()

tag_query = "SELECT * FROM gamertags"
gamerTags = pd.read_sql(tag_query, my_conn)

def get_match_data(index):
    global oldMatches, user

    user = gamerTags['User'][index]
    gamerTag = gamerTags['GamerTag'][index]
    platform = gamerTags['Platform'][index]

    try:
        print('')
        print('Exporting old matches from {}'.format(user))
        table_query = "SELECT * FROM {}".format(user.lower())
        old = pd.read_sql(table_query, my_conn)
        oldMatches = old['MatchID'].tolist()
    except MySQLdb.ProgrammingError:
        old = pd.DataFrame()
        oldMatches = []

    return gamerTag, platform

def rapid_match_extraction(a, b):

    global df

    url = "https://call-of-duty-modern-warfare.p.rapidapi.com/warzone-matches/{}/{}/".format(
        a, b)

    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

    headers = {
        'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
        'x-rapidapi-key': "e6c6bbe19amshdfe963bc74bf7dap1d5654jsn50ad5279af3c",
        'User-Agent': user_agent
    }

    response = requests.request("GET", url, headers=headers)

    data = json.loads(response.text)

    matchID = []
    gameMode = []
    kills = []
    deaths = []
    kdRatio = []

    for i in data['matches']:
        matchID.append(i['matchID'])
        gameMode.append(i['mode'])
        kills.append(i['playerStats']['kills'])
        deaths.append(i['playerStats']['deaths'])
        try:
            kdRatio.append(i['playerStats']['kdRatio'])
        except KeyError:
            kdRatio.append(int(0))

    df = pd.DataFrame()

    df['MatchID'] = matchID
    df['Mode'] = gameMode
    df['Kills'] = kills
    df['Deaths'] = deaths
    df['KDRatio'] = kdRatio

    return matchID

def get_lobby_kd(list):

    global df

    avgKD = []
    matchDate = []
    matchTime = []
    match = 1
    errors = []

    for i in list:
        if i not in oldMatches:

            print('Collecting data for {}'.format(i))
            print('')

            endpoint = "https://api.tracker.gg/api/v1/warzone/matches/{}".format(i)

            driver = webdriver.Chrome(PATH)
            driver.get(endpoint)

            body = driver.find_element_by_xpath("/html/body").text

            data = json.loads(body)

            driver.quit()

            print('Match for {} not recorded'.format(i))

            try:

                avg = next(iter(data['data']['attributes']['avgKd'].values()))

                timestamp = data['data']['metadata']['timestamp']
                dateTime = datetime.fromtimestamp(timestamp/1000)
                date = dateTime.strftime("%m-%d-%Y")
                time = dateTime.strftime("%H:%M:%S")

                print('{} - Match ID: {} | Lobby KD: {}'.format(match, i, avg))
                print('')

                matchDate.append(date)
                matchTime.append(time)
                avgKD.append(avg)
                match += 1

            except KeyError:

                avg = 0.0
                dateTime = datetime.now().timestamp()/1000
                date = datetime.now().date().strftime("%m-%d-%Y")

                print('{} - Match ID: {} | Lobby KD: {}'.format(match, i, avg))
                print('')

                matchDate.append(date)
                matchTime.append(time)
                avgKD.append(avg)
                match += 1

        else:

            print('Match for {} already in database'.format(i))
            print('')
            df = df[df['MatchID'] != i]
            df = df.reset_index().drop(columns=['index'])

        while len(errors) != 0:

            for j in errors:

                if j not in oldMatches:

                    print('Match for {} not recorded'.format(j))
                    print('')

                    endpoint = "https://api.tracker.gg/api/v1/warzone/matches/{}".format(
                        j)

                    # request = urllib.request.Request(endpoint, None, headers)
                    # response = urllib.request.urlopen(request)

                    # data = response.read()
                    # jsonData = data.decode('utf8')

                    driver = webdriver.Chrome(PATH)
                    driver.get(endpoint)

                    body = driver.find_element_by_xpath("/html/body").text

                    data = json.loads(body)

                    driver.quit()

                    errors.remove(str(j))

                    avg = list(data['data']['attributes']['avgKd'].values())[0]

                    timestamp = data['data']['metadata']['timestamp']
                    dateTime = datetime.fromtimestamp(timestamp/1000)
                    date = dateTime.strftime("%m-%d-%Y")
                    time = dateTime.strftime("%H:%M:%S")

                    print('{} - Match ID: {} | Lobby KD: {}'.format(match, i, avg))
                    print('')

                    matchDate.append(date)
                    matchTime.append(time)
                    avgKD.append(avg)
                    match += 1

    df['LobbyKD'] = avgKD
    df['Date'] = matchDate
    df['Time'] = matchTime
    df['User'] = user

    return df

def upload_matches(df):

    global user

    if len(df) != 0:

        df['MatchID'] = df['MatchID'].astype(str)
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        df.sort_values(by=['Date'], ascending=False, inplace=False)
        print('')
        print('Uploading {} to Database'.format(user))
        df.to_sql(con=my_conn, name='{}'.format(user.lower()),
                if_exists='append', index=False)

        now = datetime.now()
        date_time = now.strftime("%m-%d-%Y %H%H%S")

        savePath = 'Game History/' + str(user)

        if not os.path.exists('{}'.format(savePath)):
            print('Creating Directory for {}'.format(user))
            os.makedirs('{}'.format(savePath))

        print('')
        print('Creating game history for {}'.format(user))
        df.to_csv("{}/{}{}.csv".format(savePath, user, date_time), index=False)


for i in range(len(gamerTags))[44:]:

    username, platformID = get_match_data(i)

    matchList = rapid_match_extraction(username, platformID)

    testDf = get_lobby_kd(matchList)

    upload_matches(testDf)