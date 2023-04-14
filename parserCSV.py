import pandas as pd
import os.path
from insert_batch import insert_batch, DBobj
import re

def isname(str):
    return re.fullmatch('[a-zA-ZА-Яа-яёй\(\)\s\-]+', str)

def parseCSV(csvFileStream,  uploadfolder, mode):
    csvData = pd.read_csv(csvFileStream, sep=';')
    
    if len(csvData.columns) < 9:
        return "ERROR: not enough data for upload"
    
    columnsflags = {'lastname': 0, 'firstname':0, 'middlename':0, 'report':0, 'personalcase':0, 'year':0, 'reportfile':0, 'page':0, 'note':0}
    
    for column in csvData.columns:
        if column.lower().strip() == 'фамилия' and columnsflags['lastname'] == 0:
            csvData.rename(columns={column: 'Фамилия'}, inplace=True)
            columnsflags['lastname'] == 1
        elif column.lower().strip() == 'имя' and columnsflags['firstname'] == 0:
            csvData.rename(columns={column: 'Имя'}, inplace=True)
            columnsflags['firstname'] == 1
        elif column.lower().strip() == 'отчество' and columnsflags['middlename'] == 0:
            csvData.rename(columns={column: 'Отчество'}, inplace=True)
            columnsflags['middlename'] = 1
        elif column.lower().strip() == 'опись' and columnsflags['report'] == 0:
            csvData.rename(columns={column: 'Опись'}, inplace=True)
            columnsflags['report'] == 1
        elif column.lower().strip() == 'дело' and columnsflags['personalcase'] == 0:
            csvData.rename(columns={column: 'Дело'}, inplace=True)
            columnsflags['personalcase'] == 1
        elif column.lower().strip() == 'год' and columnsflags['year'] == 0:
            csvData.rename(columns={column: 'Год'}, inplace=True)
            columnsflags['year'] == 1
        elif column.lower().strip() == 'файл_описи' and columnsflags['reportfile'] == 0:
            csvData.rename(columns={column: 'Файл_описи'}, inplace=True)
            columnsflags['reportfile'] == 1
        elif column.lower().strip() == 'страница' and columnsflags['page'] == 0:
            csvData.rename(columns={column: 'Страница'}, inplace=True)
            columnsflags['page'] == 1
        elif column.lower().strip() == 'примечание' and columnsflags['note'] == 0:
            csvData.rename(columns={column: 'Примечение'}, inplace=True)
            columnsflags['note'] == 1
        else:
            return "incorrect column name: " + column

    batch = []
    protocol = "----- Verification with data format in file: \n\n"
    
    csvData.fillna("", inplace=True)
    for i, row in csvData.iterrows():
        
        errors = 0;
        
        if not row['Фамилия'] or (not isname(row['Фамилия'].strip())):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + " ERROR: lastname must have alphabet characters only \n"
            errors += 1
        
        if row['Имя'] and (not isname(row['Имя'].strip())):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + " ERROR: firstname must have alphabet characters only \n"
            errors += 1
            
        if row['Отчество'] and (not isname(row['Отчество'].strip())):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + " ERROR: middlename must have alphabet characters only \n"
            errors += 1
            
        # #row[3] personalcasedir
        # dirpath = ""
        # if (row[3]):
        #     dirpath = row[3]
        #     if not (os.path.isdir(dirpath)):
        #         protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + " ERROR: Directory path does not exist \n"
        #         errors += 1
        
        
        #if not row['Дело'].isdigit():
        if csvData['Дело'].dtypes != 'int64':
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + " ERROR: PersonalCase must be a number \n"
            errors += 1
        
        #if not row['Год'].isdigit():
        if csvData['Год'].dtypes != 'int64':
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + " ERROR: Year must be a number \n"
            errors += 1
         
        filepath = uploadfolder + row['Файл_описи']
        if not (os.path.isfile(filepath)):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + " ERROR: File does not exist \n"
            errors += 1

        fileformat = row['Файл_описи'].split('.')[-1]

        # if not row['Страница'].isdigit():
        if csvData['Страница'].dtypes != 'int64':
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + " ERROR: Page must be a number \n"
            errors += 1
        
        if (errors == 0):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + " PASSED verification \n"
            obj = DBobj(row['Фамилия'].strip(), row['Имя'].strip(), row['Отчество'].strip(), "", row['Примечение'], row['Опись'], row['Дело'], row['Год'], filepath, row['Страница'], fileformat)
            batch.append(obj)
        
 
    return insert_batch(batch, protocol, mode)