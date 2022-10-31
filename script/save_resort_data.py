# usage:  python script/save_resort_data.py

import pandas as pd
import sqlite3
# from project import dataproc

def save_resort_data(filepath, db_file):
    df = pd.read_csv(filepath).fillna('null')
    # print(df.head(10).to_markdown())

    conn = sqlite3.connect(db_file)
    df.to_sql(name='resorts', con=conn)

    curr = conn.execute(
        "select * from resorts limit 5")
    result = curr.fetchall()
    print(result)
    conn.close()
    print("data is saved")
    return 0

db_file = 'westunion.db'
filepath = 'data/resort.csv'

save_resort_data(filepath, db_file)