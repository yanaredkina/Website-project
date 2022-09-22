import csv
from insert_batch import insert_batch, DBobj

def csv_import(csvFileStream):
    reader = csv.reader(csvFileStream, delimiter=';')   

    batch = []

    for row in reader:
    
        if not row[0] or (not row[0].isalpha()):
            print("lastname must have alphabet characters only")
            exit(1)
        
        if row[1] and (not row[1].isalpha()):
            print("firstname must have alphabet characters only")
            exit(1)
        
        if row[2] and (not row[2].isalpha()):
            print("middlename must have alphabet characters only")
            exit(1)
        
        if not row[5].isdigit():
            print("Year must be a number")
        
        if not row[6].isdigit():
            print("Page must be a number")
        
        if row[7] != 'pdf' and row[7] != 'jpg':
            print("File type must be pdf or jpg only")
        
        obj = DBobj(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
        batch.append(obj)
    

    insert_batch(batch)
