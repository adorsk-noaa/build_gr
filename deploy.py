from jinja2 import Environment, FileSystemLoader
import tempfile
import os
import shutil
import subprocess


this_dir = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(this_dir, "assets")
templates_dir = os.path.join(this_dir, 'templates')

tpl_env = Environment(loader=FileSystemLoader(templates_dir))

"""
Check out assets.
"""
#wrangler install

"""
Assemble distribution from assets.
"""
# create distribution dir.
dist_dir = tempfile.mkdtemp(prefix="gr_dist.")
print "dd is: ", dist_dir

# Create lib dir.
lib_dir = os.path.join(dist_dir, 'lib')
os.mkdir(lib_dir)

# Copy code assets to lib dir.
georefine_lib = os.path.join(ASSETS_DIR, "georefine_py")
cmd = 'rsync -aL %s/ %s/georefine/' % (georefine_lib, lib_dir)
subprocess.call(cmd, shell=True)

# Create static files dir.
#static_dir = os.path.join(dist_dir, 'public')
#os.mkdir(static_dir)

# Assemble js/css.

# Copy to static dir.

# Copy georefine.wsgi .
wsgi_dir = os.path.join(dist_dir, 'wsgi')
os.mkdir(wsgi_dir)
shutil.copy(os.path.join(this_dir, "templates", "georefine.wsgi"),
            os.path.join(wsgi_dir, "georefine.wsgi")
           )

"""
Write config file.
"""
config_file_path = os.path.join(dist_dir, 'lib', 'georefine', 'app', 'instance', 'app_config.py')
config_file = open(config_file_path, 'wb')
tpl = tpl_env.get_template('app_config.py')
config_file.write(tpl.render())
config_file.close()


"""
Upload distribution.
"""
#@TODO

"""
Setup links on server.
"""
