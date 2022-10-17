import sqlite3
from flask import Flask, flash

class DBobj:
    def __init__(self, lastname, firstname, middlename, note, report, personalcase, year, filepath, page, filetype):
        self.lastname = lastname
        self.firstname = firstname
        self.middlename = middlename
        self.note = note
        self.report = report
        self.year = year
        self.personalcase = personalcase
        self.page = page
        self.filetype = filetype
        self.filepath = filepath
        
    def __str__(self):
        return str(self.lastname) + ' ' + str(self.firstname) + ' ' + str(self.middlename) + ' '


def insert_batch(batch, errors):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
        
    for obj in batch:
        
        try:
            cursor.execute("INSERT INTO Persons (LastName, FirstName, MiddleName, Note) VALUES (?, ?, ?, ?)",
                         (obj.lastname, obj.firstname, obj.middlename, obj.note))
            lastpersonID = cursor.lastrowid

            cursor.execute("INSERT INTO Files (Type, FilePath) VALUES (?, ?)",
                        (obj.filetype, obj.filepath))
            lastfileID = cursor.lastrowid
   
            cursor.execute("INSERT INTO Reports (Name, Year) VALUES (?, ?)",
                        (obj.report, obj.year))
            lastreportID = cursor.lastrowid
    
            cursor.execute("INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)",
                        (lastfileID, lastreportID))
                        
            cursor.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, PersonalCase, Page) VALUES (?, ?, ?, ?, ?)",
                        (lastpersonID, lastfileID, lastreportID, obj.personalcase, obj.page))
                
        
        except sqlite3.Error as e:
            errors += str(obj) + " ERROR: "+ str(e.args) + '\n'
            
    connection.commit()
    
    '''''    
    except sqlite3.Error as e:
        if connection: 
            connection.rollback()
        raise Exception(' '.join(e.args))
    
    '''   
    
    if connection: 
        connection.close()
    
    return errors