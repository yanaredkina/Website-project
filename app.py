import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from io import BytesIO

    
def ignore_case_collation(value1, value2):
    if value1.lower() == value2.lower():
        return 0
    elif value1.lower() < value2.lower():
        return -1
    else:
        return 1 

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.create_collation("NOCASE", ignore_case_collation)
    return conn
        
    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my secret key'
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = """SELECT Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, PersonRegistry.Page, Files.ID
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports on PersonRegistry.ReportID=Reports.ID 
                                            INNER JOIN Files on PersonRegistry.FileID=Files.ID 
                               WHERE Persons.LastName=? COLLATE NOCASE """
    arguments = []
    lastname = request.form['lastname']
    arguments.append(lastname)
    if 'firstname' in request.form and len(request.form['firstname']) > 0:
        firstname = request.form['firstname']
        query += 'AND Persons.FirstName=? COLLATE NOCASE '
        arguments.append(firstname)
    if 'middlename' in request.form and len(request.form['middlename']) > 0:
        middlename = request.form['middlename']
        query += 'AND Persons.MiddleName=? COLLATE NOCASE '
        arguments.append(middlename)
    conn = get_db_connection()
    registry = conn.execute(query, arguments).fetchall()
    conn.close()
    if not registry:
        flash('Ничего не найдено!')
        return redirect(url_for('index'))
    return render_template("search.html", rows = registry, arg=arguments)
    
@app.route('/content/<int:ident>')
def content(ident):
    conn = get_db_connection()
    result = conn.execute('SELECT Content, Type FROM Files WHERE ID = ?', (ident,)).fetchone()
    conn.close()
    bytes_io = BytesIO(result[0])
    if result[1] == 'jpg':
        return send_file(bytes_io, mimetype='image/jpeg')
    else: 
        return send_file(bytes_io, mimetype='application/pdf')


#####
@app.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        note = request.form['note']
        report = request.form['report']
        year = request.form['year']
        page = request.form['page']
        fileobj = request.files['file']     
        
        if not fileobj:
            flash('Нет выбранного файла')
            return render_template('upload.html')
            
        content = fileobj.read()
        
        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO Persons (LastName, FirstName, MiddleName, Note) VALUES (?, ?, ?, ?)",
                         (lastname, firstname, middlename, note))
            lastpersonID = conn.execute("SELECT id FROM Persons ORDER BY id DESC LIMIT 1").fetchone()
            
            filetype = fileobj.filename.split('.')[-1]
            conn.execute("INSERT INTO Files (Type, Content) VALUES (?, ?)",
                        (filetype, content))
            lastfileID = conn.execute("SELECT id FROM Files ORDER BY id DESC LIMIT 1").fetchone()
           
            conn.execute("INSERT INTO Reports (Name, Year) VALUES (?, ?)",
                        (report, year))
            lastreportID = conn.execute("SELECT id FROM Reports ORDER BY id DESC LIMIT 1").fetchone()
            
            conn.execute("INSERT INTO ReportRegistry (FileID, ReportID) VALUES (?, ?)",
                        (lastfileID[0], lastreportID[0]))
            conn.execute("INSERT INTO PersonRegistry (PersonID, FileID, ReportID, Page) VALUES (?, ?, ?, ?)",
                        (lastpersonID[0], lastfileID[0], lastreportID[0], page))
            
            conn.commit()
            flash("Запись успешно добавлена")
            
        except sqlite3.Error as e:
            if conn: 
                conn.rollback()
            flash("Ошибка выполнения запроса")
        
        finally:
            if conn: 
                conn.close()
            return redirect(url_for('index'))

    return render_template('upload.html')