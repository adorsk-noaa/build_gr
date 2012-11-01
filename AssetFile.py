config = {
    'CACHE_DIR': 'cache',
    'TARGET_DIR': 'assets'
}

assets = {

    'sasi_js_assets': {
        'type': 'rsync',
        'source': '/var/www/sasi.localhost/sasi_assets/js',
        'args': '--exclude **.git'
    },

    'georefine_py' : {
        'type': 'git',
        'source': 'https://github.com/adorsk-noaa/georefine.git',
        'path': 'georefine'
    },

    'georefine_client' : {
        'type': 'git',
        'source': 'https://github.com/adorsk-noaa/georefine.git',
        'path': 'georefine/app/static/GeoRefine_Assets/GeoRefineClient'
    },

    'sa_dao' : {
        'type': 'git',
        'source': 'https://github.com/adorsk-noaa/sqlalchemy_dao.git',
        'path': 'lib/sa_dao'
    },

    'flask_admin': {
        'type': 'git',
        'source': 'https://github.com/adorsk/flask-admin.git',
        'path': 'flask_admin'
    }
}
