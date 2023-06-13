import sqlite3
import csv
import os.path
import sys
from flask import Flask, render_template, request, url_for, flash, redirect, send_file, Response
from io import StringIO, BytesIO
from insert_batch import insert_batch, DBobj
from delete_report import delete_report
from update_case import update_case
from update_report import update_report
from parserCSV import parseCSV

    
app = Flask(__name__)
app.config.from_envvar('ENV_SETTINGS')
exiting = False

#app.config['SECRET_KEY'] = '192bsdfb9sf8gb9s8dhjk34twe8rsdjk43849823554727823bcbf'
#app.config['REPORTS_FOLDER'] = os.path.abspath('reports')
#app.config['PESONALCASES_FOLDER'] = os.path.abspath('personalcases')    
#app.config['ENV'] = 'development'
#app.config['DEBUG'] = True 
    
    
def sql_lower(value):
    return value.lower()

def get_db_connection():
    dbname = os.path.abspath('database.db')
    conn = sqlite3.connect(dbname)
    conn.row_factory = sqlite3.Row
    conn.create_function('sql_lower', 1, sql_lower)
    return conn
   
@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/guide')    
def guide():
    return render_template('guide.html')
    
@app.route('/search_form')
def search_form():
    return render_template('search_form.html')    

@app.route('/search', methods=['POST'])
def search():
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, 
                      Reports.Year, PersonRegistry.PersonalCase, Persons.PersonalCaseDir
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
        year = request.form['year']
        query += 'AND Reports.Year = ' + year
    
    query += ' ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName'
    conn = get_db_connection()
    result = conn.execute(query, arguments).fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return redirect(url_for('search_form'))
    
    return render_template('search_results.html', rows=result, arg=arguments, total=len(result))

@app.route('/search_ID/<int:ident>')
def search_ID(ident):
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Persons.PersonalCaseDir, 
                      Reports.Name, Reports.Year, PersonRegistry.Page, PersonRegistry.PersonalCase, Files.ID, Files.Type
                            FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                         INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID 
                                         LEFT JOIN Files ON PersonRegistry.FileID=Files.ID 
                            WHERE Persons.ID = ? 
                            ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName """          
                       
    conn = get_db_connection()
    result = conn.execute(query, (ident,)).fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return redirect(url_for('search_form'))
    
    arguments = [result[0][1], result[0][2], result[0][3]]
    return render_template('display_results.html', rows=result, arg=arguments) 

@app.route('/content/<int:ident>')
def content(ident):
    conn = get_db_connection()
    result = conn.execute('SELECT FileName, Type FROM Files WHERE ID = ?', (ident,)).fetchone()
    conn.close()
    
    fullfilepath = os.path.join(app.config['REPORTS_FOLDER'], result[0])
    if not (os.path.isfile(fullfilepath)):
        message = 'НЕВОЗМОЖНО ОТОБРАЗИТЬ ФАЙЛ ОПИСИ: УКАЗАННОГО В БД ФАЙЛА НЕТ НА ДИСКЕ! (' + (fullfilepath) + ')'
        return Response(message, mimetype='text/plain')
        
    if result[1] == 'jpg' or result[1] =='jpeg':
        return send_file(fullfilepath, mimetype='image/jpeg')
    if result[1] == 'tif' or result[1] == 'tiff':
        return send_file(fullfilepath, mimetype='image/tiff')
    if result[1] =='png':
        return send_file(fullfilepath, mimetype='image/png')
    if result[1] =='gif':
        return send_file(fullfilepath, mimetype='image/gif')
    else:
        return send_file(fullfilepath, mimetype='application/pdf')  

@app.route('/reports/<char>/<year>/<int:page>', methods=['POST', 'GET'])
def reports(char, year, page):
    if request.method == 'POST':
        year = request.form.get('select_year')
        
    query = """SELECT Persons.ID, Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, 
                      Reports.Year, PersonRegistry.PersonalCase, Persons.PersonalCaseDir
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID
                               WHERE sql_lower(Persons.LastName) LIKE ? """
    
    if (year != '*'):
        query += ' AND Reports.Year = ' + year 
    if (char != '%'):
        args = char + '%'
    else:
        args = char 
    
    query += ' ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName'
    
    conn = get_db_connection()
    result = conn.execute(query, (args, )).fetchall()
    years = conn.execute('SELECT Reports.Year FROM Reports ORDER BY Reports.Year').fetchall()
    conn.close()
    if not result:
        flash('Ничего не найдено!')
        return render_template('reports.html', rows=result, arg=[char, year], years=years, pages=[0], curpage=0, total=0)
        
    pages_cnt = (len(result) // 60 + 1, len(result) // 60)[bool(len(result) % 60 == 0)]
    pages = [ i for i in range(1, pages_cnt + 1)]
    start = (page - 1) * 60
    end = start + 60

    return render_template('reports.html', rows=result[start:end], arg=[char, year], years=years, pages=pages, curpage=page, total=len(result))
    
@app.route('/download_report/<ftype>/<char>/<year>')
def download_report(ftype, char, year):
    conn = get_db_connection()
    query = """SELECT Persons.LastName, Persons.FirstName, Persons.MiddleName, Reports.Name, PersonRegistry.PersonalCase,
                      Reports.Year, Files.FileName, PersonRegistry.Page, Persons.Note, Persons.PersonalCaseDir
                               FROM Persons INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID 
                                            INNER JOIN Reports ON PersonRegistry.ReportID=Reports.ID 
                                            LEFT JOIN Files ON PersonRegistry.FileID=Files.ID 
                               WHERE sql_lower(Persons.LastName) LIKE ? """
    
    if (year != '*'):
         query += ' AND Reports.Year = ' + year
    query += ' ORDER BY Persons.LastName, Persons.FirstName, Persons.MiddleName '
    result = conn.execute(query, (char + '%', )).fetchall()
    conn.close()
    
    proxy = StringIO()
    writer = csv.writer(proxy, delimiter=';')
    writer.writerow(['Фамилия', 'Имя', 'Отчество', 'Опись', 'Дело', 'Год', 'Файл_описи', 'Страница', 'Примечание', 'Папка_дела'])
    writer.writerows(result)
    mem = BytesIO()
    mem.write(proxy.getvalue().encode())
    mem.seek(0)
    proxy.close()
    
    if (ftype == 'csv'):
        mimetype = 'text/csv'
        filename = 'report.csv'
    else:
        mimetype = 'text/plain'
        filename = 'report.txt'
        
    return send_file(mem, as_attachment=True, download_name=filename, mimetype=mimetype)

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
            protocol = parseCSV(stream, app.config['REPORTS_FOLDER'], app.config['PESONALCASES_FOLDER'], 'test')
        else:
            protocol = parseCSV(stream, app.config['REPORTS_FOLDER'], app.config['PESONALCASES_FOLDER'], 'prod')
        return Response(protocol, mimetype='text/plain', headers={'Content-Disposition':'attachment; filename=uploadprotocol.txt'})
        
    return render_template('upload_batch.html')
    
@app.route('/delete_form', methods=['GET', 'POST'])
def delete_form():
    query = 'SELECT Reports.ID, Reports.Name, Reports.Year FROM Reports ORDER BY Reports.Year'
    conn = get_db_connection()
    result = conn.execute(query).fetchall()
    conn.close()
    
    if request.method == 'POST':
        reportid = request.form.get('select_report')
        if not reportid:
            flash('Опись не выбрана')
            return render_template('delete_form.html', rows = result)
        
        protocol = delete_report(reportid)
        return Response(protocol, mimetype='text/plain', headers={'Content-Disposition':'attachment; filename=deleteprotocol.txt'})
    
    return render_template('delete_form.html', rows=result)    

@app.route('/display_directory/<year>/<directory>')
def display_directory(year, directory):
    dirpath = os.path.join(app.config['PESONALCASES_FOLDER'], year, directory)
    if not os.path.exists(dirpath):
        message = 'НЕВОЗМОЖНО ПЕРЕЙТИ В ПАПКУ ЛИЧНОГО ДЕЛА: УКАЗАННОЙ В БД ПАПКИ НЕТ НА ДИСКЕ! (' + (dirpath) + ')'
        return Response(message, mimetype='text/plain')


    files = list(map(lambda x: (x.encode('utf8', 'surrogateescape').decode('utf8'), x.split('.')[-1]), os.listdir(dirpath)))
    return render_template('display_directory.html', files=files, directory=directory, year=year)

@app.route('/dircontent/<year>/<directory>/<filename>')
def dircontent(year, directory, filename):
    dirpath = os.path.join(app.config['PESONALCASES_FOLDER'], year, directory)
    fd = open(os.path.join(dirpath, filename).encode('utf8'), 'br')
    
    filetype = filename.split('.')[-1]
    if filetype == 'jpg' or filetype =='jpeg' or filetype == 'JPEG' or filetype == 'JPG':
        return send_file(fd, mimetype='image/jpeg')
    if filetype == 'tif' or filetype == 'tiff' or filetype == 'TIFF' or filetype == 'TIF':
        return send_file(fd, mimetype='image/tiff')
    if filetype =='png' or filetype == 'PNG':
        return send_file(fd, mimetype='image/png')
    if filetype =='gif' or filetype == 'GIF':
        return send_file(fd, mimetype='image/gif')
    else:
        return send_file(fd, mimetype='application/pdf')

@app.route('/update_case_form', methods=['GET', 'POST'])
def update_case_form():
    if request.method == 'POST':
        lastname = request.form['lastname']
        report = request.form['report']
        year = request.form['year']
        case = request.form['case']
        casedir = request.form['casedir']
        
        query = """SELECT Persons.ID FROM Persons 
                    INNER JOIN PersonRegistry ON Persons.ID=PersonRegistry.PersonID
                    INNER JOIN Reports on PersonRegistry.ReportID=Reports.ID
                    WHERE sql_lower(Persons.LastName) = ? AND Reports.Name = ? AND Reports.Year = ? AND PersonRegistry.PersonalCase = ? """
        
        conn = get_db_connection()
        result = conn.execute(query, (sql_lower(lastname), report, year, case)).fetchone()
        conn.close()   
        if not result:
            flash('Студент в БД не найден!')
            return render_template('update_case_form.html')
        
        dirpath = os.path.join(app.config['PESONALCASES_FOLDER'], year, casedir)
        if not os.path.exists(dirpath): 
            flash('Папка не найдена!')
            return render_template('update_case_form.html')
                
        protocol = update_case(result[0], casedir)
        return Response(protocol, mimetype='text/plain', headers={'Content-Disposition':'attachment; filename=updateprotocol.txt'})

    return render_template('update_case_form.html')

@app.route('/update_report_form', methods=['GET', 'POST'])
def update_report_form():
    
    query = 'SELECT Reports.ID, Reports.Name, Reports.Year FROM Reports ORDER BY Reports.Year'
    conn = get_db_connection()
    result = conn.execute(query).fetchall()
    conn.close()
    
    if request.method == 'POST':
        reportid = request.form.get('select_report')
        if not reportid:
            flash('Опись не выбрана')
            return render_template('update_report_form.html', rows = result)
        
        report_filename = request.form['report_file'] 
        fullfilepath = os.path.join(app.config['REPORTS_FOLDER'], report_filename)
        if not os.path.exists(fullfilepath): 
            flash('Файл не найден!')
            return render_template('update_report_form.html', rows = result)
        
        protocol = update_report(reportid, report_filename)
        return Response(protocol, mimetype='text/plain', headers={'Content-Disposition':'attachment; filename=updateprotocol.txt'})
    
    return render_template('update_report_form.html', rows=result)

@app.route('/shutdown')
def shutdown():
    global exiting
    exiting = True
    return "Done"

@app.teardown_request
def teardown(exception):
    if exiting:
        os._exit(0)
    
#if __name__ == "__main__":
#    app.run()