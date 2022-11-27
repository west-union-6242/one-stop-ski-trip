import sqlite3
import pandas as pd
import csv
import numpy
import geopy
from scipy import spatial
from geopy import distance
from geopy.geocoders import Nominatim
import math
import requests
import json
import os

# The calculate_similarity function will calculate how similar any resort is given one resort. 1 being the most similar.
def calculate_similarity(resort,df):
  #print('User chose '+resort+'calculating similarity')
  # Select resort info (row) based on user selected resort
  row = df.loc[df['resort_name'] == resort]
  #print(row)
  lastcol = df.columns.get_loc("black_acres")
  #print(lastcol)
  firstcol = df.columns.get_loc("summit")
  dataset1 = row.iloc[:, firstcol:lastcol+1].values.tolist()[0]
  #print(dataset1)
  rownum = df.index[df.resort_name == resort][0]
  for i in range(len(df)):
    each = df.loc[i].values.tolist()
    #print(each)
    dataset2 = each[firstcol:lastcol+1]
    #print('2',dataset2)
    result = 1 - spatial.distance.cosine(dataset1, dataset2)
    #print(result)
    #df['similarity'][i] = result
    df.loc[i, 'similarity']= round(result,2)
  return df

# The calculate_neighbors function will calculate the number of resorts within 50 miles of the given resort.
def calculate_neighbors(resort,df):
  #print('User chose '+resort+'calculating number of neighbors')
  df['neighbor_num'] = 0
  # Select resort info (row) based on user selected resort
  row = df.loc[df['resort_name'] == resort]
  latcol = df.columns.get_loc("lat")
  loncol = df.columns.get_loc("lon")
  #print(loncol)
  resort1loc = tuple(row.iloc[:, latcol:loncol+1].values.tolist()[0])
  #print(resort1loc)
  if math.isnan(resort1loc[0]) or math.isnan(resort1loc[1]):
    pass
  for i in range(len(df)):
    each = df.loc[i].values.tolist()
    resort2loc = tuple(each[latcol:loncol+1])
    if math.isnan(resort2loc[0]) or math.isnan(resort2loc[1]):
      continue
    d = distance.great_circle(resort1loc, resort2loc).miles
    #print(d)
    if d < 50:
      df.loc[i,'neighbor_num'] +=1
  newdf = df
  return newdf

# The get_weather function will use weather api to first get the grid info then weather forecast info for the next 12 hrs based on the lat and lon of the resort.
def get_weather(lat,lon):
  if math.isnan(lat) or math.isnan(lon):
    pass
  else:
    weatherdata = None
    trynummax = 20
    trynum=0
    while trynum <= trynummax:
        try:
            add = '/'+str(lat)+','+str(lon)
            response_API = requests.get('https://api.weather.gov/points'+add)
            data = response_API.text
            parse_json = json.loads(data)
            gridId = str(parse_json['properties']['gridId'])
            gridX = str(parse_json['properties']['gridX'])
            gridY = str(parse_json['properties']['gridY'])
            add2 = gridId + '/'+gridX+','+gridY+'/forecast'
            response_API2 = requests.get('https://api.weather.gov/gridpoints/'+add2)
            data2 = response_API2.text
            parse_json2 = json.loads(data2)
            weatherdata = parse_json2['properties']['periods']
            weathertable = pd.DataFrame.from_dict(weatherdata)
            return weathertable[['name','temperature','temperatureUnit','windSpeed','detailedForecast']][1:2]
        except:
            trynum +=1
            print("API connection failed, try again...")
            pass
    return pd.DataFrame(columns=['name','temperature','temperatureUnit','windSpeed','detailedForecast'])

# The resort_recommender function will calculate the most suitable 5 resorts based on user input.
def resort_recommender(difficulty, goal, fav_resort, exppts, goalpts, resortpts):
  #print('User answered: ', difficulty, goal, fav_resort)
  #print(os.getcwd())
  # Get the new dataframe newdf with similarity column added
  df = pd.read_csv ('data/resort.csv')
  df.loc[:,'similarity']=0
  newdf = calculate_similarity(fav_resort,df)
  #print(newdf['similarity'])
  # Rank newdf based on experience_level, goal and resort inputs
  if difficulty == 'beginner':
    colexp = 'green_percent'
  elif difficulty == 'intermediate':
    colexp = 'blue_percent'
  else:
    colexp = 'black_percent'
  if goal == 'goal_a':
    colgoal = 'green_acres'
  elif goal == 'goal_b':
    colgoal = 'runs'
  elif goal == 'goal_c':
    colgoal = 'vertical'
  elif goal == 'goal_d':
    colgoal = 'neighbor_num'
    newdf = calculate_neighbors(fav_resort,newdf)
  newdf.loc[:,'goal_rank'] = newdf[colgoal].rank()
  newdf.loc[:,'exp_rank'] = newdf[colexp].rank()
  newdf.loc[:,'resort_rank'] = newdf['similarity'].rank()
  newdf.loc[:, 'totalpts']= newdf['exp_rank']*int(exppts) + newdf['goal_rank']*int(goalpts) + newdf['resort_rank']*int(resortpts)
  fdf = newdf.nlargest(5, 'totalpts')
  #loclist = list(zip(fdf.lat, fdf.lon))
  results = fdf[['resort_name', 'summit','base','vertical','lifts','runs','acres','green_acres','blue_acres','black_acres','lat','lon']]
  wf = pd.DataFrame()
  results['12hr_temperature (F)']=0
  results['12hr_forecast (details)']=0
  #print(results)
  for index, row in results.iterrows():
    rlat = row['lat']
    rlon = row['lon']
    wf=get_weather(rlat,rlon)
    fc = wf['detailedForecast'].values[0]
    tf = wf['temperature'].values
    results.loc[index,'12hr_temperature (F)']=tf
    results.loc[index,'12hr_forecast (details)']=fc
  results = results.drop(columns=['lat', 'lon'])
  results = results.rename(columns={"summit": "summit_elevation (ft)", "vertical": "vertical_drop (ft)", "base":"base_elevation (ft)","green_acres":"green_trail (acres)","blue_acres":"blue_trail (acres)","black_acres":"black_trail (acres)"})
  results['lifts'] = results['lifts'].astype('int')
  results['runs'] = results['runs'].astype('int')
  return results
