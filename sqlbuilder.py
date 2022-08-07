class SQLBuilder:
    def __init__(self, exactMatch, caseInsensitive):
        self.query = ""
        self.exactMatch = exactMatch
        self.caseInsensitive = caseInsensitive
        self.arguments = []
        self.whereAdded = false
    
    def select(self, columns):
        self.query += "SELECT" + ", ".join(columns)
        return self

    def from(self, table):
        self.query += " FROM " + table
        return self

    def innerJoin(self, other, on):
        self.query += "INNER JOIN " + other + " " + on
        return self
    
    def matches(self):
        if self.exactMatch:
            return " = ? "
        else:
            return " LIKE ? "

    def normalizeColumn(self, value):
        if self.caseInsensitive:
            return " sql_lower(" + value ") "
        else:
            return " " + value + " "

    def normalizeValue(self, value):
        if self.caseInsensitive:
            return sql_lower(value)
        else:
            return value

    def where(self, column, to):
        if self.whereAdded:
            self.query += " AND "
        else:
            self.query += " WHERE "
            self.whereAdded = true
        self.query += self. normalizeColumn(column) + self.matches()
        self.arguments.append(self.normalizeValue(to))

def sql_lower(value):
    return value.lower()



@app.route('/search', methods=['POST'])
def search():
     if request.form.get('exactMatch'):
        builder = SQLBuilder(true, true)

    else:
        builder = SQLBuilder(false, true)
    
    builder.select(["Persons.LastName", "Persons.FirstName", "Persons.MiddleName", "Reports.Name", "PersonRegistry.Page", "Files.ID"])
    builder.from("Persons")
    builder.innerJoin("PersonRegistry", "Persons.ID=PersonRegistry.PersonID")
    builder.innerJoin("Reports", "PersonRegistry.ReportID=Reports.ID ")
    builder.innerJoin("Files", "PersonRegistry.FileID=Files.ID")           
        
    lastname = request.form['lastname']
    builder.where("Persons.LastName", lastname)

    if 'firstname' in request.form and len(request.form['firstname']) > 0:
        firstname = request.form['firstname']
        builder.where("Persons.FirstName", firstname)
    if 'middlename' in request.form and len(request.form['middlename']) > 0:
        middlename = request.form['middlename']
        builder.where("Persons.MiddleName", middlename)

    conn = get_db_connection()
    registry = conn.execute(builder.query, builder.arguments).fetchall()
    conn.close()
    if not registry:
        flash('Ничего не найдено!')
        return redirect(url_for('index'))
    return render_template("search.html", rows = registry, arg=arguments)
    
