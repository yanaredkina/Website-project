import sqlite3
import os.path
from flask import Flask, flash


def update_case(person_id, casedir):
    connection = sqlite3.connect(os.path.abspath('database.db'))
    cursor = connection.cursor()
    
    protocol = ''
        
    try:
        cursor.execute('UPDATE Persons SET (PersonalCaseDir) = (?) WHERE ID = ? ', (casedir, person_id))                  
    
    except sqlite3.Error as e:
        protocol += 'ERROR: '+ str(e.args) + '\n'
    
    else:
        protocol += '\nUPDATE COMLETED\n'
        connection.commit()
    
    
    if connection:
        cursor.close()
        connection.close()
        
    return protocol