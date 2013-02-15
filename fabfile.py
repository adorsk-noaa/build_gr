from fabric.api import *
from jinja2 import Environment, FileSystemLoader
import tempfile
import os
import shutil
import subprocess
import time

#env.user = 'georefine'
#env.hosts = ['192.168.33.10']
env.user = 'sasi'
env.hosts = ['128.128.104.193']
remote_releases_dir = "~/apps/georefine/releases"
remote_persistent_dir = "~/apps/georefine/persistent"
remote_tmp = '/tmp'

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

    # Create python dir.
    py_dir = os.path.join(dist_dir, 'python')
    os.mkdir(py_dir)

    # Copy code assets to lib dir.
    georefine_lib = os.path.join(ASSETS_DIR, "georefine")
    cmd = 'rsync -aL %s/ %s/georefine/' % (georefine_lib, py_dir)
    subprocess.call(cmd, shell=True)

    for lib in ['sa_dao', 'task_manager']:
        lib_path = os.path.join(ASSETS_DIR, lib)
        cmd = 'rsync -aL %s/ %s/%s/' % (lib_path, py_dir, lib)
        subprocess.call(cmd, shell=True)

    # Create static files dir.
    static_dir = os.path.join(dist_dir, 'html')
    os.mkdir(static_dir)

    # Make static assets dir.
    gr_static_assets_dir = os.path.join(static_dir, GR_ASSETS_DIR_NAME)
    os.mkdir(gr_static_assets_dir)

    # Copy georefine client.
    grc_dir = os.path.join(gr_static_assets_dir, 'GeoRefineClient')
    shutil.copytree(os.path.join(ASSETS_DIR, "georefine_client"), grc_dir)

    # Build GeoRefineClient.
    grc_target_dir = os.path.join(grc_dir)
    build_grc(target_dir=grc_target_dir)

    # Copy georefine.wsgi.
    #wsgi_dir = os.path.join(dist_dir, 'wsgi')
    #os.mkdir(wsgi_dir)
    #shutil.copy(os.path.join(this_dir, "templates", "georefine.wsgi"),
                #os.path.join(wsgi_dir, "georefine.wsgi")
               #)

    """
    Write config file.
    """
    #config_file_path = os.path.join(dist_dir, 'lib', 'georefine', 'app', 'instance', 'app_config.py')
    #config_file = open(config_file_path, 'wb')
    #tpl = tpl_env.get_template('app_config.py')
    #config_file.write(tpl.render())
    #config_file.close()

    """
    Upload distribution.
    """
    archive = shutil.make_archive(dist_dir, 'gztar', dist_dir)
    remote_dist_target = os.path.join(remote_tmp, os.path.basename(archive))
    put(archive, remote_dist_target)

    """
    Unpack on the server.
    """
    release_dir = os.path.join(remote_releases_dir, "rel.%s" % time.time())
    run('mkdir %s; cd %s; tar -xzf %s' % (release_dir, release_dir, remote_dist_target))

    """
    Set permissions.
    """
    #run('chmod a+x %s/wsgi/georefine.wsgi' % release_dir)

    """
    Make symlinks.
    """
    current_release_dir = "%s/current" % remote_releases_dir
    run('ln -nsf %s %s' % (release_dir, current_release_dir))
    run('ln -nsf %s/app_config.py %s/python/georefine/app/instance/app_config.py' % (
        remote_persistent_dir, current_release_dir))
    #run('ln -nsf %s/lib ~/lib' % release_dir)
    #run('ln -nsf %s/wsgi/georefine.wsgi ~/wsgi/georefine.wsgi;' % release_dir)
    #run('ln -nsf %s/public/%s ~/public/%s' % (release_dir, GR_ASSETS_DIR_NAME, GR_ASSETS_DIR_NAME))

@task
def build_grc(target_dir=None):
    """ Build the GeoRefineClient project."""
    # Fetch assets.
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if not target_dir:
        target_dir = os.path.join(os.path.dirname(__file__), "dist",
                                "georefine_client")

    # Make build dir.
    build_dir = tempfile.mkdtemp(prefix="grcBuild.")

    # Copy GRC to build dir.
    shutil.copytree(
        os.path.join(assets_dir, 'georefine_client'), 
        os.path.join(build_dir, 'georefine_client'), 
    )
    # Link assets.
    link_cmd = "mkdir %s/georefine_client/assets; ln -s %s/js %s/georefine_client/assets/js;" % (
        build_dir, assets_dir, build_dir)
    subprocess.call(link_cmd, shell=True)

    # Run build.
    build_cmd = "node %s/georefine_client/build.js" % build_dir
    subprocess.call(build_cmd, shell=True)

    # Copy dist to local dist, after clearing.
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)
    dist_dir = os.path.join(target_dir, 'dist')
    shutil.copytree("%s/georefine_client/dist" % build_dir, dist_dir)

    # Copy specific assets to dist dir.
    target_assets_dir = os.path.join(target_dir, 'assets', 'js')
    os.makedirs(target_assets_dir)
    for asset in ['jquery.js', 'jReject']:
        asset_source_path = os.path.join(assets_dir, 'js', asset)
        cmd = 'rsync -a %s %s' % (asset_source_path, target_assets_dir)
        subprocess.call(cmd, shell=True)

    # Remove build dir.
    shutil.rmtree(build_dir)
