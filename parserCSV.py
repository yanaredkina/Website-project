import pandas as pd
import os.path
from insert_batch import insert_batch, DBobj
import re

def isname(str):
    return re.fullmatch('[a-zA-ZА-Яа-яёй\(\)\s\-]+', str)
    

def parseCSV(csvFileStream,  reportfolder, casefolder, mode):
    csvData = pd.read_csv(csvFileStream, sep=';', dtype=object)
    
    if len(csvData.columns) < 10:
        return 'ERROR: not enough column for upload'
    
    columnsflags = {'lastname': 0, 'firstname':0, 'middlename':0, 'report':0, 'personalcase':0, 'year':0, 'reportfile':0, 'page':0, 'note':0, 'casedir': 0}
    
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
            csvData.rename(columns={column: 'Примечание'}, inplace=True)
            columnsflags['note'] == 1
        elif column.lower().strip() == 'папка_дела' and columnsflags['casedir'] == 0:
            csvData.rename(columns={column: 'Папка_дела'}, inplace=True)
            columnsflags['note'] == 1
        else:
            return 'incorrect column name: ' + column

    batch = []
    protocol = '----- Verification with data format in file: \n\n'
    
    csvData.fillna('', inplace=True)

    for i, row in csvData.iterrows():
        
        errors = 0;
        
        if not row['Фамилия'] or (not isname(row['Фамилия'].strip())):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '   ERROR: Lastname must have alphabet characters only \n'
            errors += 1
        
        if row['Имя'] and (not isname(row['Имя'].strip())):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '   ERROR: Firstname must have alphabet characters only \n'
            errors += 1
            
        if row['Отчество'] and (not isname(row['Отчество'].strip())):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '   ERROR: Middlename must have alphabet characters only \n'
            errors += 1
        
        if not row['Опись']: 
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '   ERROR: Report is empty \n'
            errors += 1
            
        if not row['Дело'] or (not row['Дело'].isdigit()):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '   ERROR: PersonalCase must be a number \n'
            errors += 1
        
        if not row['Год'] or (not row['Год'].isdigit()):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '   ERROR: Year must be a number \n'
            errors += 1
         
        if row['Файл_описи']:
            filepath = os.path.join(reportfolder, row['Файл_описи'])
            if not (os.path.isfile(filepath)):
                protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '   ERROR: File does not exist \n'
                errors += 1
            else:
                fileformat = row['Файл_описи'].split('.')[-1].lower()
        else:
            fileformat = ''
        

        if not row['Страница'].isdigit():
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '   ERROR: Page must be a number \n'
            errors += 1
        
        if row['Папка_дела']:
            dirpath = os.path.join(casefolder, str(row['Год']), row['Папка_дела'])
            if not (os.path.exists(dirpath)):
                protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '   ERROR: Personal directory does not exist \n'
                errors += 1
            
        if (errors == 0):
            protocol += row['Фамилия'] + ' ' + row['Имя'] + ' ' + row['Отчество'] + '       PASSED verification \n'
            obj = DBobj(row['Фамилия'].strip(), row['Имя'].strip(), row['Отчество'].strip(), row['Папка_дела'], row['Примечание'], row['Опись'], row['Дело'], row['Год'], row['Файл_описи'], row['Страница'], fileformat)
            batch.append(obj)
        
 
    return insert_batch(batch, protocol, mode)