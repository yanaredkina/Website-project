import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, send_file, Response
from insert_batch import insert_batch, DBobj
from csv_import import csv_import
import csv
from io import StringIO
        
def sql_lower(value):
    return value.lower()

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    conn.create_function("sql_lower", 1, sql_lower)
    return conn
    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my secret key'
app.config['UPLOAD_FOLDER'] = 'documents/'
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = """SELECT Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, PersonRegistry.Page, Files.ID
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports on PersonRegistry.ReportID=Reports.ID 
                                            INNER JOIN Files on PersonRegistry.FileID=Files.ID 
                               WHERE sql_lower(Persons.LastName) """
    
    if request.form.get('exactMatch'):
        s = lambda x: sql_lower(x)
        q = ' = ? '
    else:
        s = lambda x: '%' + sql_lower(x) + '%'
        q = ' LIKE ? '           
        
    arguments = []
    lastname = request.form['lastname']
    query += q
    arguments.append(s(lastname))
    if 'firstname' in request.form and len(request.form['firstname']) > 0:
        firstname = request.form['firstname']
        query += 'AND sql_lower(Persons.FirstName) ' + q
        arguments.append(s(firstname))
    if 'middlename' in request.form and len(request.form['middlename']) > 0:
        middlename = request.form['middlename']
        query += 'AND sql_lower(Persons.MiddleName) ' + q
        arguments.append(s(middlename))
    
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
    result = conn.execute('SELECT FilePath, Type FROM Files WHERE ID = ?', (ident,)).fetchone()
    conn.close()
    if result[1] == 'jpg':
        return send_file(result[0], mimetype='image/jpeg')
    else: 
        return send_file(result[0], mimetype='application/pdf')



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
            
        filepath = app.config['UPLOAD_FOLDER'] + fileobj.filename
        fileobj.save(filepath)
        filetype = fileobj.filename.split('.')[-1]
            
        obj = DBobj(lastname, firstname, middlename, note, report, year, page, filetype, filepath)
        batch = [obj]
        
        try: 
            insert_batch(batch)
            flash("Запись успешно добавлена")
            return redirect(url_for('index'))
        
        except Exception as error:
            flash("Ошибка выполнения запроса: ")
            flash(' '.join(error.args))
            return render_template('upload.html')

    return render_template('upload.html')

@app.route('/upload_batch', methods=('GET', 'POST'))
def upload_batch():
    if request.method == 'POST':
        fileobj = request.files['file']  
        if not fileobj:
            flash('Нет выбранного файла')
            return render_template('upload_batch.html')
        
        if (fileobj.filename.split('.')[-1] != 'csv'):
            flash('Файл неверного формата')
            return render_template('upload_batch.html')
        
        bytes = fileobj.read().decode('utf8')
        stream = StringIO(bytes)
        try:
            csv_import(stream)
            flash("Пакет успешно добавлен")
            return redirect(url_for('index'))
            
        except Exception as error:
            flash("Ошибка выполнения запроса: ")
            flash(' '.join(error.args))
            return render_template('upload_batch.html')
        
    return render_template('upload_batch.html')
    
    
@app.route('/all', methods=['GET'])
def all():
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName
                               FROM Persons
                               GROUP BY Persons.ID"""
    conn = get_db_connection()
    result = conn.execute(query).fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return redirect(url_for('index'))
    return render_template("all.html", rows = result)
    

@app.route('/search_ID/<int:ident>')
def search_ID(ident):
    query = """SELECT Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, PersonRegistry.Page, Files.ID
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports on PersonRegistry.ReportID=Reports.ID 
                                            INNER JOIN Files on PersonRegistry.FileID=Files.ID 
                               WHERE Persons.ID = ? """          
                               
    conn = get_db_connection()
    result = conn.execute(query, (ident,)).fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return redirect(url_for('index'))
    arguments = [result[0][0], result[0][1], result[0][2]]
    return render_template("search.html", rows = result, arg=arguments)
    
    
@app.route('/download_report/<ftype>')
def download_report(ftype):
    conn = get_db_connection()
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName
                               FROM Persons
                               GROUP BY Persons.ID"""
    result = conn.execute(query).fetchall()
    conn.close()
    
    
    if (ftype == 'csv'):
        output = StringIO()
        writer = csv.writer(output)
        mimetype = "text/csv"
        filename = "report.csv"
    
        for row in result:
            line = [str(row[1]) + ';' + str(row[2]) + ';' + str(row[3])]
            writer.writerow(line)
        output.seek(0)
    
    else:
        output = ""
        for row in result:
            output += str(row[1]) + ' ' + str(row[2]) + ' ' + str(row[3]) + '\n'
        mimetype = "text/plain"
        filename = "report.txt"
    
    return Response(output, mimetype=mimetype, headers={"Content-Disposition":"attachment; filename=%s" %filename})
    