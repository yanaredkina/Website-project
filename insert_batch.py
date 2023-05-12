import sqlite3
import os.path
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
        
def sql_lower(value):
    return value.lower()
    

def insert_batch(batch, protocol, mode):
    connection = sqlite3.connect(os.path.abspath('database.db'))
    connection.create_function('sql_lower', 1, sql_lower)
    cursor = connection.cursor()
    
    protocol += '----- ERRORS when uploading to the database: \n\n'
    rowcount = 0
    
    for obj in batch:
        
        try:
            query = """SELECT Persons.ID FROM Persons 
                        INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID
                        INNER JOIN Reports on PersonRegistry.ReportID=Reports.ID
                        WHERE sql_lower(Persons.LastName) = ? AND sql_lower(Persons.FirstName) = ? AND sql_lower(Persons.MiddleName) = ?
                                AND Reports.Name = ? AND Reports.Year = ? AND PersonRegistry.PersonalCase = ? """
                                                                                                
            args = (sql_lower(obj.lastname), sql_lower(obj.firstname), sql_lower(obj.middlename), obj.report, obj.year, obj.personalcase)
            exist = cursor.execute(query, args).fetchone()
            
            if exist:
                protocol += str(obj) + '    is already in the database\n'
                continue
            
            cursor.execute('INSERT INTO Persons (LastName, FirstName, MiddleName, PersonalCaseDir, Note) VALUES (?, ?, ?, ?, ?)',
                         (obj.lastname, obj.firstname, obj.middlename, obj.personalcasedir, obj.note))
            lastpersonID = cursor.lastrowid
            rowcount += 1
            
            
            exist = cursor.execute('SELECT ID FROM Files WHERE FilePath = ? ', (obj.filepath, )).fetchone()
            if not exist:
                cursor.execute('INSERT INTO Files (Type, FilePath) VALUES (?, ?)',
                            (obj.filetype, obj.filepath))
                fileID = cursor.lastrowid
            else:
                fileID = exist[0]
                
                
            exist = cursor.execute('SELECT ID FROM Reports WHERE Name = ? AND Year = ? ', (obj.report, obj.year)).fetchone()
            if not exist:
                cursor.execute('INSERT INTO Reports (Name, Year) VALUES (?, ?)',
                            (obj.report, obj.year))
                reportID = cursor.lastrowid
            else:
                reportID = exist[0]


            exist = cursor.execute('SELECT ID FROM ReportRegistry WHERE FileID = ? AND ReportID = ? ', (fileID, reportID)).fetchone()
            if not exist:
                cursor.execute('INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)',
                            (fileID, reportID))
            
            
            cursor.execute('INSERT INTO PersonRegistry (PersonID, FileID, ReportID, PersonalCase, Page) VALUES (?, ?, ?, ?, ?)',
                        (lastpersonID, fileID, reportID, obj.personalcase, obj.page))

        
        except sqlite3.Error as e:
            protocol += str(obj) + '    ERROR: '+ str(e.args) + '\n'
        
        else:
            if (mode == 'prod'):
                connection.commit()
    
    protocol += str(rowcount) + ' persons was added\n'

    if connection:
        cursor.close()
        connection.close()
    
    return protocol