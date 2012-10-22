from fabric.api import *
from jinja2 import Environment, FileSystemLoader
import tempfile
import os
import shutil
import subprocess
import time

env.user = 'georefine'
env.hosts = ['192.168.33.10']

this_dir = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(this_dir, "assets")
templates_dir = os.path.join(this_dir, 'templates')
tpl_env = Environment(loader=FileSystemLoader(templates_dir))

def deploy():
    """
    Check out assets.
    """
    #wrangler install

    """
    Assemble distribution from assets.
    """
    # create distribution dir.
    dist_container = tempfile.mkdtemp(prefix="gr_dist.")
    dist_dir = os.path.join(dist_container, "georefine_dist.%s" % os.getpid())
    os.mkdir(dist_dir)

    # Create lib dir.
    lib_dir = os.path.join(dist_dir, 'lib')
    os.mkdir(lib_dir)

    # Copy code assets to lib dir.
    georefine_lib = os.path.join(ASSETS_DIR, "georefine_py")
    cmd = 'rsync -aL %s/ %s/georefine/' % (georefine_lib, lib_dir)
    subprocess.call(cmd, shell=True)

    for lib in ['sa_dao', 'flask_admin']:
        lib_path = os.path.join(ASSETS_DIR, lib)
        cmd = 'rsync -aL %s/ %s/%s/' % (lib_path, lib_dir, lib)
        subprocess.call(cmd, shell=True)

    # Create static files dir.
    static_dir = os.path.join(dist_dir, 'public')
    os.mkdir(static_dir)

    # Make static assets dir.
    static_assets_dir = os.path.join(static_dir, "assets")
    os.mkdir(static_assets_dir)

    #@TODO: optimize js/css.

    # Populate js assets.
    js_assets_dir = os.path.join(ASSETS_DIR, 'sasi_js_assets')
    cmd = 'rsync -aL %s/ %s/js/' % (js_assets_dir, static_assets_dir)
    subprocess.call(cmd, shell=True)

    # Write require.js config.

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
    remote_tmp = '~/tmp'
    archive = shutil.make_archive(dist_dir, 'gztar', dist_dir)
    remote_dist_target = os.path.join(remote_tmp, os.path.basename(archive))
    put(archive, remote_dist_target)

    """
    Unpack on the server.
    """
    remote_releases_dir = "~/releases"
    release_dir = os.path.join(remote_releases_dir, "rel.%s" % time.time())
    run('cd ~/releases; mkdir %s; cd %s; tar -xzf %s' % (release_dir, release_dir, remote_dist_target))

    """
    Set permissions.
    """
    run('chmod a+x %s/wsgi/georefine.wsgi' % release_dir)

    """
    Make symlinks.
    """
    run('ln -nsf %s/lib ~/lib' % release_dir)
    run('ln -nsf %s/wsgi/georefine.wsgi ~/wsgi/georefine.wsgi;' % release_dir)
    run('ln -nsf %s/public/assets ~/public/assets' % release_dir)
