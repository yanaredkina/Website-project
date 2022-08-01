import sqlite3
from flask import Flask, flash

def insert_batch(batch):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()


    try:
        
        for i in range(len(batch)):
            
            obj = batch[i]
        
            cursor.execute("INSERT INTO Persons (LastName, FirstName, MiddleName, Note) VALUES (?, ?, ?, ?)",
                         (obj.lastname, obj.firstname, obj.middlename, obj.note))
            lastpersonID = cursor.lastrowid
        
            filetype = obj.fileobj.filename.split('.')[-1]
            content = obj.fileobj.read()

            cursor.execute("INSERT INTO Files (Type, Content) VALUES (?, ?)",
                        (filetype, content))
            lastfileID = cursor.lastrowid
       
            cursor.execute("INSERT INTO Reports (Name, Year) VALUES (?, ?)",
                        (obj.report, obj.year))
            lastreportID = cursor.lastrowid
        
            cursor.execute("INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)",
                        (lastfileID, lastreportID))
            cursor.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
                        (lastpersonID, lastfileID, lastreportID, obj.page))
                    
        connection.commit()
        flash("Запись успешно добавлена")
        
    except sqlite3.Error as e:
        if connection: 
            connection.rollback()
        flash("Ошибка выполнения запроса")
    
    finally:
        if connection: 
            connection.close()