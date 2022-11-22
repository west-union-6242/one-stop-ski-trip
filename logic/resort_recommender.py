import sqlite3
import pandas as pd

def resort_recommender(difficulty, goal, fav_resort):
    conn = sqlite3.connect('westunion.db')
    curr = conn.execute(
        "select * from resorts limit 5")
    resorts = curr.fetchall()
    column_names = ['index', 'Resort', 'State', 'Summit', 'Base', 'Vertical',
                                                                           'Lifts', 'Runs', 'Acres', 'Green Percent', 'Green Acres',
                                                                           'Blue Percent', 'Blue Acres', 'Black Percent', 'Black Acres',
                                                                           'Lat', 'Lon']
    resorts_df = pd.DataFrame(resorts, columns = column_names)
    resorts_df.drop('index', axis=1, inplace=True)
    return resorts_df


