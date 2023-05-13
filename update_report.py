import sqlite3
import os.path
from flask import Flask, flash


def update_report(reportid, report_filename):
    connection = sqlite3.connect(os.path.abspath('database.db'))
    cursor = connection.cursor()
    
    protocol = ''
        
    try:
        exist = cursor.execute('SELECT FileID FROM ReportRegistry WHERE ReportID = ? ', (reportid, )).fetchone()
        if exist:
            protocol += 'Report already with file in DB\nPlease go to DELETE + INSERT method instead\n'     
            
        else:
            cursor.execute('INSERT INTO Files (Type, FileName) VALUES (?, ?)',
                        (report_filename.split('.')[-1].lower(), report_filename))
            fileid = cursor.lastrowid
        
        
            cursor.execute('INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)',
                        (fileid, reportid))
        
        
            cursor.execute('UPDATE PersonRegistry SET (FileID) = (?) WHERE ReportID = ?',
                        (fileid, reportid))
        
            protocol += '\nUPDATE COMLETED\n'
    
    except sqlite3.Error as e:
        protocol += 'ERROR: '+ str(e.args) + '\n'
    
    else:
        connection.commit()
    
    
    if connection:
        cursor.close()
        connection.close()
        
    return protocol