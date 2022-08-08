import csv
from insert_batch import insert_batch, DBobj

with open('some.csv', newline='') as f:
    reader = csv.reader(f, delimiter=',')
    batch = []
    
    for row in reader:
        
        if not row[0] or (not row[0].isalpha()):
            print("lastname must have alphabet characters only")
            exit(1)
            
        if row[1] and (not row[0].isalpha()):
            print("firstname must have alphabet characters only")
            exit(1)
            
        if row[2] and (not row[0].isalpha()):
            print("middlename must have alphabet characters only")
            exit(1)
            
        if not row[5].isdigit():
            print("Year must be a number")
            
        if not row[6].isdigit():
            print("Page must be a number")
            
        if row[7] != 'pdf' and row[7] != 'jpg':
            print("File type must be pdf or jpg only")
        
        with open(row[8], 'rb') as file:
            content = file.read()
            
        obj = DBobj(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], content)
        batch.append(obj)
        
    
    insert_batch(batch)