import sqlite3

connection = sqlite3.connect('database.db')
connection.text_factory = str

with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO Persons (LastName, FirstName, MiddleName) VALUES (?, ?, ?)",
            ('Петров', 'Петр', 'Петрович')
            )

cur.execute("INSERT INTO Persons (LastName, FirstName, MiddleName) VALUES (?, ?, ?)",
            ('Романов', 'Роман', 'Романович')
            )
            
cur.execute("INSERT INTO Persons (LastName, FirstName, MiddleName) VALUES (?, ?, ?)",
            ('Иванов', 'Иван', 'Иванович')
            )

cur.execute("INSERT INTO Persons (LastName, FirstName, MiddleName) VALUES (?, ?, ?)",
            ('Сидоров', 'Николай', 'Николаевич')
            )
            
cur.execute("INSERT INTO Persons (LastName, FirstName, MiddleName) VALUES (?, ?, ?)",
            ('Кузнецов', 'Виктор', 'Викторович')
            )
            
cur.execute("INSERT INTO Persons (LastName, FirstName, MiddleName) VALUES (?, ?, ?)",
            ('Иванов', 'Игорь', 'Игоревич')
            )
            
cur.execute("INSERT INTO Persons (LastName, FirstName, MiddleName) VALUES (?, ?, ?)",
            ('Романов', 'Роман', 'Сергеевич')
            )
            
                        

cur.execute("INSERT INTO Files (Type, FilePath) VALUES (?, ?)",
            ('pdf', 'documents/report1.pdf')
            )

cur.execute("INSERT INTO Files (Type, FilePath) VALUES (?, ?)",
            ('jpg', 'documents/report2_1.jpg')
            )
            
cur.execute("INSERT INTO Files (Type, FilePath) VALUES (?, ?)",
            ('jpg', 'documents/report2_2.jpg')
            )
            
cur.execute("INSERT INTO Files (Type, FilePath) VALUES (?, ?)",
            ('jpg', 'documents/report2_3.jpg')
            )

cur.execute("INSERT INTO Files (Type, FilePath) VALUES (?, ?)",
            ('jpg', 'documents/report3_1.jpg')
            )



cur.execute("INSERT INTO Reports (Name, Year) VALUES (?, ?)",
            ('Отчет 1', 1980)
            )

cur.execute("INSERT INTO Reports (Name, Year) VALUES (?, ?)",
            ('Отчет 2', 1981)
            )
            
cur.execute("INSERT INTO Reports (Name, Year) VALUES (?, ?)",
            ('Отчет 3', 1982)
            )
            


cur.execute("INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)",
            (1, 1)
            )
            
cur.execute("INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)",
            (2, 2)
            )

cur.execute("INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)",
            (3, 2)
            )
            
cur.execute("INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)",
            (4, 2)
            )

cur.execute("INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)",
            (5, 3)
            )                
                 
            
cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (1, 1, 1, 2)
            )
            
cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (1, 5, 3, 1)
            )
            
cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (2, 3, 2, 2)
            )

cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (2, 5, 3, 1)
            ) 

cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (3, 1, 1, 1)
            ) 
            
cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (3, 2, 2, 1)
            ) 
            
cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (3, 5, 3, 1)
            ) 
            
cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (4, 2, 2, 1)
            ) 
            
cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (5, 3, 2, 2)
            ) 
            
cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (6, 4, 2, 3)
            ) 
            
cur.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
            (7, 4, 2, 3)
            ) 
                     
connection.commit()
connection.close()