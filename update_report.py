import sqlite3
import os.path
from flask import Flask, flash


def update_report(reportid, report_file):
    connection = sqlite3.connect(os.path.abspath('database.db'))
    cursor = connection.cursor()
    
    protocol = ''
        
    try:
        exist = cursor.execute('SELECT FileID FROM ReportRegistry WHERE ReportID = ? ', (reportid, )).fetchone()
        if exist:
            protocol += 'Report already with file in DB\n PLEASE GO TO DELETE + INSERT METHOD INSTEAD\n'
        
        else:
            exist = cursor.execute('SELECT ID FROM Files WHERE FilePath = ? ', (report_file, )).fetchone()
            if exist:
                protocol += 'File with name ' + report_file + ' is already in the database with ID=' + str(exist[0]) + '\n'
            
            else:
                cursor.execute('INSERT INTO Files (Type, FilePath) VALUES (?, ?)',
                            (report_file.split('.')[-1], report_file))
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