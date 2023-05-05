import sqlite3
import os.path

connection = sqlite3.connect(os.path.abspath('database.db'))
connection.text_factory = str

with open(os.path.abspath('schema.sql')) as f:
    connection.executescript(f.read())
                     
connection.commit()
connection.close()