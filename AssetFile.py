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
        'source': 'https://github.com/adorsk-noaa/georefine.git'
    }
}
