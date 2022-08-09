import argparse
from insert_batch import insert_batch, DBobj
        

parser = argparse.ArgumentParser(description='Process input data for sql-insert')

parser.add_argument('--lastname', dest='lastname', type=str, required=True)
parser.add_argument('--firstname', dest='firstname', type=str, default = '')
parser.add_argument('--middlename', dest='middlename', type=str, default = '')
parser.add_argument('--note', dest='note', type=str, default = '')
parser.add_argument('--report', dest='report', type=str, required=True)
parser.add_argument('--year', dest='year', type=int, required=True)
parser.add_argument('--page', dest='page', type=int, required=True)
parser.add_argument('--filetype', dest='filetype', choices=['pdf', 'jpg'])
parser.add_argument('--path', dest='path', type=str, required=True)

args = parser.parse_args()

if not args.lastname.isalpha():
    print("lastname must have alphabet characters only")
    exit(1)
    
if args.firstname and (not args.firstname.isalpha()):
    print("firstname must have alphabet characters only")
    exit(1)
    
if args.middlename and (not args.middlename.isalpha()):
    print("middlename must have alphabet characters only")
    exit(1)

with open(args.path, 'rb') as file:
    content = file.read()

obj = DBobj(args.lastname, args.firstname, args.middlename, args.note, args.report, args.year, args.page, args.filetype, content)
batch = [obj]
        
insert_batch(batch)
