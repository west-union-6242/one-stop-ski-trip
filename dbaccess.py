
import sqlite3
from sqlite3 import Error
import csv

class dataproc():
    def create_connection(self, path):
        self.connection = None
        try:
            self.connection = sqlite3.connect(path)
            self.connection.text_factory = str
        except Error as e:
            print("Error:" + str(e))
        return self.connection

    def execute_query(self, query):
        try:
            assert query != "", "Query Blank"
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
        except Error as e:
            print("Error:" + str(e))
        return None

    def close(self):
        try:
            self.connection.close()
        except Error as e:
            print("Error:" + str(e))
        return None

