import sys
import site 
import os


# Get file's parent dir.
parent_dir  = os.path.dirname(os.path.apspath(__file__))

# Define dirs to include.
lib_dirs = [
    # App libs.
    os.path.join(parent_dir, '..', 'libs'),
    # VirtualEnv libs
    #@TODO: a way to get the python version??
    os.path.join(parent_dir, '..', 'venv/lib/python2.6/site-packages'),
]

# Remember original sys.path.
prev_sys_path = list(sys.path) 

# Add each new lib directory.
for lib_dir in lib_dirs:
    site.addsitedir(lib_dir)

# Reorder sys.path so new directories at the front.
new_sys_path = [] 
for item in list(sys.path): 
    if item not in prev_sys_path: 
        new_sys_path.append(item) 
        sys.path.remove(item) 
sys.path[:0] = new_sys_path 

# Import the application.
from georefine.app import app as application
