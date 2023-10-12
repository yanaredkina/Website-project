import webbrowser
import sys
import os
import subprocess
import time
  
# if run script place is outside project folder - need to change dir path: 
#dir = os.path.join(os.path.dirname(sys.argv[0]), 'Project')
#os.chdir(dir)
dir = os.path.dirname(sys.argv[0])
os.environ['ENV_SETTINGS'] = os.path.join(dir, 'env.cfg')
subprocess.Popen(["flask","run"], stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL, stderr=subprocess.STDOUT)
time.sleep(2)

webbrowser.open_new('http://127.0.0.1:5000/')