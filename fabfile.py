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
GR_ASSETS_DIR_NAME = "GeoRefine_Assets"
templates_dir = os.path.join(this_dir, 'templates')
tpl_env = Environment(loader=FileSystemLoader(templates_dir))

@task
def deploy():
    """
    Check out assets.
    """
    #wrangler install

    """
    Build distribution from assets.
    """
    # create dist dir.
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

    # Copy georefine.wsgi.
    wsgi_dir = os.path.join(dist_dir, 'wsgi')
    os.mkdir(wsgi_dir)
    shutil.copy(os.path.join(this_dir, "templates", "georefine.wsgi"),
                os.path.join(wsgi_dir, "georefine.wsgi")
               )

    # Create static files dir.
    static_dir = os.path.join(dist_dir, 'public')
    os.mkdir(static_dir)

    # Make static assets dir.
    gr_static_assets_dir = os.path.join(static_dir, GR_ASSETS_DIR_NAME)
    os.mkdir(gr_static_assets_dir)

    # Copy georefine client.
    grc_dir = os.path.join(gr_static_assets_dir, 'GeoRefineClient')
    shutil.copytree(os.path.join(ASSETS_DIR, "georefine_client"), grc_dir)

    # Build GeoRefineClient.
    grc_dist_dir = os.path.join(grc_dir, 'dist')
    build_grc(dist_dir=grc_dist_dir)

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
    run('ln -nsf %s/public/%s ~/public/%s' % (release_dir, GR_ASSETS_DIR_NAME,
                                              GR_ASSETS_DIR_NAME))

@task
def build_grc(dist_dir=None):
    """ Build the GeoRefineClient project."""
    # Fetch assets.
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not dist_dir:
        dist_dir = os.path.join(os.path.dirname(__file__), "dist",
                                "georefine_client")

    # Make build dir.
    build_dir = tempfile.mkdtemp(prefix="grcBuild.")
    # Copy GRC to build dir.
    shutil.copytree(
        os.path.join(assets_dir, 'georefine_client'), 
        os.path.join(build_dir, 'georefine_client'), 
    )
    # Link assets.
    link_cmd = "mkdir %s/georefine_client/assets; ln -s %s %s/georefine_client/assets/js;" % (
        build_dir, assets_dir, build_dir)
    subprocess.call(link_cmd, shell=True)

    # Run build.
    build_cmd = "node %s/georefine_client/build.js" % build_dir
    subprocess.call(build_cmd, shell=True)

    # Copy dist to local dist, after clearing.
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    shutil.copytree("%s/georefine_client/dist" % build_dir, dist_dir)

    # Remove build dir.
    shutil.rmtree(build_dir)
