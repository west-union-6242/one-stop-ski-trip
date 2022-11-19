import sqlite3

def resort_recommender(difficulty, goal, fav_resort):
    conn = sqlite3.connect('westunion.db')
    curr = conn.execute(
        "select * from resorts limit 5")
    resorts = curr.fetchall()
    return resorts