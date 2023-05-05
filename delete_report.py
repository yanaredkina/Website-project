import sqlite3
import os.path
from flask import Flask, flash


def delete_report(report_id):
    connection = sqlite3.connect(os.path.abspath('database.db'))
    cursor = connection.cursor()
    
    protocol = ""
        
    try:
        files = cursor.execute("SELECT FileID FROM ReportRegistry WHERE ReportID = ? ",
                  (report_id, )).fetchall()
                  
        cursor.execute("DELETE FROM ReportRegistry WHERE ReportID = ? ",
                     (report_id, ))
                    
        persons = cursor.execute("SELECT PersonID FROM PersonRegistry WHERE ReportID = ? ",
                     (report_id, )).fetchall()
        
        cursor.execute("DELETE FROM PersonRegistry WHERE ReportID = ? ",
                     (report_id, ))
        
        cursor.execute("DELETE FROM Reports WHERE ID = ? ",
                     (report_id, ))
                     
        cursor.executemany("DELETE FROM Files WHERE ID in (?) ", files)
        
        cursor.executemany("DELETE FROM Persons WHERE ID in (?) ", persons)
        protocol += str(cursor.rowcount) + " persons was deleted\n"                   
    
    except sqlite3.Error as e:
        protocol += "ERROR: "+ str(e.args) + '\n'
    
    else:
        protocol += "\nDELETING COMLETED\n"
        connection.commit()
    
    
    if connection:
        cursor.close()
        connection.close()
        
    return protocol