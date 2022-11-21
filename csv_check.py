import csv
import os.path
from insert_batch import insert_batch, DBobj

def csv_check(csvFileStream, uploadfolder, mode):
    reader = csv.reader(csvFileStream, delimiter=';')   

    batch = []
    protocol = "----- Verification with data format in file: \n\n"
    errors = 0;
    

    for row in reader:
        
        #row[0] fisrtname
        if not row[0] or (not row[0].isalpha()):
            protocol += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: lastname must have alphabet characters only \n"
            errors += 1
        
        #row[1] lastname
        if row[1] and (not row[1].isalpha()):
            protocol += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: firstname must have alphabet characters only \n"
            errors += 1
            
        #row[2] middlename
        if row[2] and (not row[2].isalpha()):
            protocol += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: middlename must have alphabet characters only \n"
            errors += 1
            
        #row[3] personalcasedir 
        dirpath = ""
        if (row[3]):
            dirpath = row[3]
            if not (os.path.isdir(dirpath)):
                protocol += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: Directory path does not exist \n"
                errors += 1
        
        #row[4] notes
        #row[5] reportnumber
        
        #row[6] personalCase number
        if not row[6].isdigit():
            protocol += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: PersonalCase must be a number \n"
            errors += 1
        
        #row[7] year
        if not row[7].isdigit():
            protocol += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: Year must be a number \n"
            errors += 1
         
        #row[8] filepath 
        filepath = uploadfolder + row[8]
        if not (os.path.isfile(filepath)):
            protocol += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: File does not exist \n"
            errors += 1

        fileformat = row[8].split('.')[-1]
        
        #row[9] page
        if not row[9].isdigit():
            protocol += row[0] + ' ' + row[1] + ' ' + row[2] + " ERROR: Page must be a number \n"
            errors += 1
        
        if (errors == 0):
            protocol += row[0] + ' ' + row[1] + ' ' + row[2] + " PASSED verification \n"
            obj = DBobj(row[0], row[1], row[2], dirpath, row[4], row[5], row[6], row[7], filepath, row[9], fileformat)
            batch.append(obj)
        

 
    return insert_batch(batch, protocol, mode)
