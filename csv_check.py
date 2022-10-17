import csv
import os.path
from insert_batch import insert_batch, DBobj

def csv_check(csvFileStream):
    reader = csv.reader(csvFileStream, delimiter=';')   

    batch = []
    errors = ""
    

    for row in reader:

        if not row[0] or (not row[0].isalpha()):
            errors += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: lastname must have alphabet characters only \n"
            continue
    
        if row[1] and (not row[1].isalpha()):
            errors += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: firstname must have alphabet characters only \n"
            continue
    
        if row[2] and (not row[2].isalpha()):
            errors += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: middlename must have alphabet characters only \n"
            continue
    
        if not row[5].isdigit():
            errors += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: PersonalCase must be a number \n"
            continue
        
        if not row[6].isdigit():
            errors += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: Year must be a number \n"
            continue
            
        filepath = "documents/" + row[7]
        if not (os.path.isfile(filepath)):
            errors += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: File does not exist \n"
            continue

        fileformat = row[7].split('.')[-1]
        
        if not row[8].isdigit():
            errors += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: Page must be a number \n"
            continue
        
        
        obj = DBobj(row[0], row[1], row[2], row[3], row[4], row[5], row[6], filepath, row[8], fileformat)
        batch.append(obj)
        
        
    return insert_batch(batch, errors)
