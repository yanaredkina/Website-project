import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, send_file, Response
from insert_batch import insert_batch, DBobj
from csv_check import csv_check
from parserCSV import parseCSV
from delete_report import delete_report
import csv
import os.path
from io import StringIO, BytesIO
#from pandoc.types import *
#pip install comtypes
#import comtypes.client 
      
def sql_lower(value):
    return value.lower()

def get_db_connection():
    dbname = os.path.abspath('database.db')
    conn = sqlite3.connect(dbname)
    conn.row_factory = sqlite3.Row
    conn.create_function("sql_lower", 1, sql_lower)
    return conn
    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my secret key'
app.config['UPLOAD_FOLDER'] = os.path.abspath('documents')
app.config['PESONALCASES_FOLDER'] = os.path.abspath('personalcases')
app.config['ENV'] = 'development'
app.config['DEBUG'] = True
    
@app.route('/')
def index():
    return render_template('index.html')
    
    
@app.route('/search_form')
def search_form():
    return render_template('search_form.html')
    

@app.route('/search', methods=['POST'])
def search():
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, Reports.Year, PersonRegistry.PersonalCase
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports on PersonRegistry.ReportID=Reports.ID
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
        
    if 'year' in request.form and len(request.form['year']) > 0:
        print("here")
        year = request.form['year']
        query += 'AND Reports.Year = ' + year
    
    query += " ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName "
    conn = get_db_connection()
    result = conn.execute(query, arguments).fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return redirect(url_for('search_form'))
    return render_template("search_results.html", rows = result, arg=arguments, total = len(result))

    
@app.route('/content/<int:ident>')
def content(ident):
    conn = get_db_connection()
    result = conn.execute('SELECT FilePath, Type FROM Files WHERE ID = ?', (ident,)).fetchone()
    conn.close()
    fullfilepath = os.path.join(app.config['UPLOAD_FOLDER'], result[0])
    if result[1] == 'jpg':
        return send_file(fullfilepath, mimetype='image/jpeg')
    else: 
        return send_file(fullfilepath, mimetype='application/pdf')


@app.route('/all/')
def all():
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, Reports.Year, PersonRegistry.PersonalCase
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID
                               ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName 
                               """
    
    conn = get_db_connection()
    result = conn.execute(query).fetchall()
    years = conn.execute("""SELECT Reports.Year FROM Reports""").fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return redirect(url_for('index'))
    return render_template("all.html", rows = result, arg =['%', '*'], years = years, total = len(result))
  
    

@app.route('/search_ID/<int:ident>')
def search_ID(ident):
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Persons.PersonalCaseDir, Reports.Name, Reports.Year, PersonRegistry.Page, PersonRegistry.PersonalCase, Files.ID, Files.Type
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID 
                                            INNER JOIN Files ON PersonRegistry.FileID=Files.ID 
                               WHERE Persons.ID = ? 
                               ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName """          
                               
    conn = get_db_connection()
    result = conn.execute(query, (ident,)).fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return redirect(url_for('search'))
    arguments = [result[0][1], result[0][2], result[0][3]]
    return render_template("display_results.html", rows = result, arg=arguments)
    
    
@app.route('/download_report/<ftype>/<char>/<year>')
def download_report(ftype, char, year):
    conn = get_db_connection()
    query = """SELECT Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, PersonRegistry.PersonalCase, Reports.Year, Files.FilePath, PersonRegistry.Page, Persons.Note
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID 
                                            INNER JOIN Files ON PersonRegistry.FileID=Files.ID 
                               WHERE sql_lower(Persons.LastName) LIKE ? 
                               """
    
    if (year != '*'):
         query += " AND Reports.Year = " + year
    
    query += " ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName "
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
        
    return send_file(mem, as_attachment=True, download_name=filename, mimetype=mimetype)

# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     if request.method == 'POST':
#         lastname = request.form['lastname']
#         firstname = request.form['firstname']
#         middlename = request.form['middlename']
#         personalcasedir = request.form['personalcasedir']
#         note = request.form['note']
#         report = request.form['report']
#         year = request.form['year']
#         personalcase = request.form['personalcase']
#         page = request.form['page']
#         fileobj = request.files['file']
#
#         #add cheking personalcasedir
#
#         if not fileobj:
#             flash('Нет выбранного файла')
#             return render_template('upload.html')
#
#         filepath = app.config['UPLOAD_FOLDER'] + fileobj.filename
#         fileobj.save(filepath)
#         filetype = fileobj.filename.split('.')[-1]
#
#         obj = DBobj(lastname, firstname, middlename, personalcasedir, note, report, personalcase, year, filepath, page, filetype)
#         batch = [obj]
#
#         try:
#             insert_batch(batch)
#             flash("Запись успешно добавлена")
#             return redirect(url_for('search_form'))
#
#         except Exception as error:
#             flash("Ошибка выполнения запроса: ")
#             flash(' '.join(error.args))
#             return render_template('upload.html')
#
#     return render_template('upload.html')


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
            protocol = parseCSV(stream, app.config['UPLOAD_FOLDER'], 'test')
        else:
            protocol = parseCSV(stream, app.config['UPLOAD_FOLDER'], 'prod')
        return Response(protocol, mimetype="text/plain", headers={"Content-Disposition":"attachment; filename=uploadprotocol.txt"})
        
    return render_template('upload_batch.html')
    

@app.route('/filter_by_char/<char>/<year>')
def filter_by_char(char, year):
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, Reports.Year, PersonRegistry.PersonalCase
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID 
                               WHERE sql_lower(Persons.LastName) LIKE ? 
                               """
    if (year != '*'):
         query += " AND Reports.Year = " + year
         
    query += " ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName"
    
    conn = get_db_connection()
    result = conn.execute(query, (char + '%', )).fetchall()
    years = conn.execute("""SELECT Reports.Year FROM Reports""").fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
    
    return render_template("all.html", rows = result, arg = [char, year], years = years, total = len(result))
    
    

@app.route('/filter_by_year/<char>', methods=['POST'])
def filter_by_year(char):
    year = request.form.get('select_year')
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, Reports.Year, PersonRegistry.PersonalCase
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID 
                               WHERE sql_lower(Persons.LastName) LIKE ? 
                               """
    if (year != '*'):
         query += " AND Reports.Year = " + year
    
    query += " ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName"
    
    conn = get_db_connection()
    result = conn.execute(query, (char + '%', )).fetchall()
    years = conn.execute("""SELECT Reports.Year FROM Reports""").fetchall()
    conn.close()
        
    if not result:
        flash('Ничего не найдено!')

    return render_template("all.html", rows = result, arg = [char, year], years = years, total = len(result))
    
    
@app.route('/guide')    
def guide():
    return render_template("guide.html")
    
    

@app.route('/delete_form', methods=['GET', 'POST'])
def delete_form():
    if request.method == 'POST':
        reportid = request.form.get('select_report')
        protocol = delete_report(reportid)
        return Response(protocol, mimetype="text/plain", headers={"Content-Disposition":"attachment; filename=deleteprotocol.txt"})
    

    query = """SELECT Reports.ID, Reports.Name, Reports.Year
                               FROM Reports"""
    conn = get_db_connection()
    result = conn.execute(query).fetchall()
    conn.close()
    return render_template("delete_form.html", rows = result)
    

@app.route('/display_directory/<directory>')
def display_directory(directory):
    dirpath = os.path.join(app.config['PESONALCASES_FOLDER'], directory)
    if not os.path.exists(dirpath): 
        flash('Ничего не найдено!')
        return render_template("index.html")

    files = list(map(lambda x: (x.encode('utf8', 'surrogateescape').decode('utf8'), x.split('.')[-1]), os.listdir(dirpath)))
    return render_template('display_directory.html', files=files, directory=directory)


@app.route('/dircontent/<directory>/<filename>')
def dircontent(directory, filename):
    dirpath = os.path.join(app.config['PESONALCASES_FOLDER'], directory)
    fd = open(os.path.join(dirpath, filename).encode('utf8'), 'br')
    return send_file(fd, mimetype='image/jpeg')

#update Persons set (PersonalCaseDir) = ('Vassiliev') WHERE ID = 5059;

@app.route('/display_by_page/<offset>')
def display_by_page(offset):
    if (offset == '0'):
        startflag = True
    else:
        startflag = False
    
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, Reports.Year, PersonRegistry.PersonalCase
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID
                               ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName 
                               LIMIT ?, 60 """
    
    conn = get_db_connection()
    result = conn.execute(query, (offset, )).fetchall()
    offset = int(offset) + len(result)
    conn.close()
    
    if not result:
        finishflag = True
    else:
        finishflag = False
    return render_template("display_by_page.html", rows = result, offset = offset, start = startflag, finish = finishflag)  

    
if __name__ == "__main__":
    app.run()
