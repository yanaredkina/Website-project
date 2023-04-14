import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, send_file, Response
from insert_batch import insert_batch, DBobj
from csv_check import csv_check
from parserCSV import parseCSV
import csv
import os.path
from io import StringIO, BytesIO
  
      
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
    
    
@app.route('/search_form')
def search_form():
    return render_template('search.html')
    

@app.route('/search', methods=['POST'])
def search():
    query = """SELECT Persons.LastName, Persons.FirstName, Persons.MiddleName, Persons.PersonalCaseDir, Reports.Name, Reports.Year, PersonRegistry.Page, PersonRegistry.PersonalCase, Files.ID, Files.Type
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
        return redirect(url_for('search_form'))
    return render_template("search_results.html", rows = registry, arg=arguments)

    
@app.route('/content/<int:ident>')
def content(ident):
    conn = get_db_connection()
    result = conn.execute('SELECT FilePath, Type FROM Files WHERE ID = ?', (ident,)).fetchone()
    conn.close()
    if result[1] == 'jpg':
        return send_file(result[0], mimetype='image/jpeg')
    else: 
        return send_file(result[0], mimetype='application/pdf')


@app.route('/all')
def all():
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, Reports.Year, PersonRegistry.PersonalCase
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID
                               GROUP BY Persons.ID
                               ORDER BY Persons.LastName """
    conn = get_db_connection()
    result = conn.execute(query).fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return redirect(url_for('index'))

    return render_template("all.html", rows = result, arg =['%'])
  
    

@app.route('/search_ID/<int:ident>')
def search_ID(ident):
    query = """SELECT Persons.LastName, Persons.FirstName, Persons.MiddleName, Persons.PersonalCaseDir, Reports.Name, Reports.Year, PersonRegistry.Page, PersonRegistry.PersonalCase, Files.ID, Files.Type
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID 
                                            INNER JOIN Files ON PersonRegistry.FileID=Files.ID 
                               WHERE Persons.ID = ? """          
                               
    conn = get_db_connection()
    result = conn.execute(query, (ident,)).fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return redirect(url_for('search'))
    arguments = [result[0][0], result[0][1], result[0][2]]
    return render_template("search_results.html", rows = result, arg=arguments)
    
    
@app.route('/download_report/<ftype>,<char>')
def download_report(ftype, char):
    conn = get_db_connection()
    query = """SELECT Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, PersonRegistry.PersonalCase, Reports.Year, Files.FilePath, PersonRegistry.Page, Persons.Note
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID 
                                            INNER JOIN Files ON PersonRegistry.FileID=Files.ID 
                               WHERE sql_lower(Persons.LastName) LIKE ? 
                               ORDER BY Persons.LastName"""
    result = conn.execute(query, (char + '%', )).fetchall()
    conn.close()
    
    proxy = StringIO()
    writer = csv.writer(proxy)
    writer.writerow(['Фамилия', 'Имя', 'Отчество', 'Опись', 'Дело', 'Год', 'Файл описи', 'Страница', 'Примечание'])
    writer.writerows(result)
    mem = BytesIO()
    mem.write(proxy.getvalue().encode())
    mem.seek(0)
    proxy.close()
    
    if (ftype == 'csv'):
        mimetype = "text/csv"
        filename = "report.csv"
    else:
        mimetype = "text/plain"
        filename = "report.txt"
        
    return send_file(mem, as_attachment=True, attachment_filename=filename, mimetype=mimetype)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        lastname = request.form['lastname']
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        personalcasedir = request.form['personalcasedir']
        note = request.form['note']
        report = request.form['report']
        year = request.form['year']
        personalcase = request.form['personalcase']
        page = request.form['page']
        fileobj = request.files['file']
        
        #add cheking personalcasedir
        
        if not fileobj:
            flash('Нет выбранного файла')
            return render_template('upload.html')
            
        filepath = app.config['UPLOAD_FOLDER'] + fileobj.filename
        fileobj.save(filepath)
        filetype = fileobj.filename.split('.')[-1]
            
        obj = DBobj(lastname, firstname, middlename, personalcasedir, note, report, personalcase, year, filepath, page, filetype)
        batch = [obj]
        
        try: 
            insert_batch(batch)
            flash("Запись успешно добавлена")
            return redirect(url_for('search_form'))
        
        except Exception as error:
            flash("Ошибка выполнения запроса: ")
            flash(' '.join(error.args))
            return render_template('upload.html')

    return render_template('upload.html')


@app.route('/upload_batch', methods=['GET', 'POST'])
def upload_batch():
    if request.method == 'POST':
        mode = request.form.get('mode')
        fileobj = request.files['file']  
        if not fileobj:
            flash('Нет выбранного файла')
            return render_template('upload_batch.html')
        
        if (fileobj.filename.split('.')[-1] != 'csv'):
            flash('Файл неверного формата')
            return render_template('upload_batch.html')
        
        bytes = fileobj.read().decode('utf8')
        stream = StringIO(bytes)
        
        if (mode == 'test'):
            #protocol = csv_check(stream, app.config['UPLOAD_FOLDER'], 'test')
            protocol = parseCSV(stream, app.config['UPLOAD_FOLDER'], 'test')
        else:
            #protocol = csv_check(stream, app.config['UPLOAD_FOLDER'], 'prod')
            protocol = parseCSV(stream, app.config['UPLOAD_FOLDER'], 'prod')
        return Response(protocol, mimetype="text/plain", headers={"Content-Disposition":"attachment; filename=uploadprotocol.txt"})
        
    return render_template('upload_batch.html')
    

@app.route('/display_by_char/<char>')
def display_by_char(char):
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, Reports.Year, PersonRegistry.PersonalCase
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID 
                               WHERE sql_lower(Persons.LastName) LIKE ? 
                               GROUP BY Persons.ID
                               ORDER BY Persons.LastName """
    
    conn = get_db_connection()
    result = conn.execute(query, (char + '%', )).fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
    return render_template("all.html", rows = result, arg = [char])