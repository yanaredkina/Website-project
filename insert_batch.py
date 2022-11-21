import sqlite3
from flask import Flask, flash

class DBobj:
    def __init__(self, lastname, firstname, middlename, personalcasedir, note, report, personalcase, year, filepath, page, filetype):
        self.lastname = lastname
        self.firstname = firstname
        self.middlename = middlename
        self.personalcasedir = personalcasedir
        self.note = note
        self.report = report
        self.year = year
        self.personalcase = personalcase
        self.page = page
        self.filetype = filetype
        self.filepath = filepath
        
    def __str__(self):
        return str(self.lastname) + ' ' + str(self.firstname) + ' ' + str(self.middlename) + ' '


def insert_batch(batch, protocol, mode):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    protocol += "----- ERRORS when uploading to the database: \n\n"
    
    for obj in batch:
        
        try:
            cursor.execute("INSERT INTO Persons (LastName, FirstName, MiddleName, PersonalCaseDir, Note) VALUES (?, ?, ?, ?, ?)",
                         (obj.lastname, obj.firstname, obj.middlename, obj.personalcasedir, obj.note))
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
            protocol += str(obj) + " ERROR: "+ str(e.args) + '\n'
        
        else:
            if (mode == 'prod'):
                connection.commit()
    

    if connection:
        cursor.close()
        connection.close()
    
    return protocol