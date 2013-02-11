config = {
    'CACHE_DIR': 'cache',
    'TARGET_DIR': 'assets'
}

assets = {
    'georefine' : {
        'type': 'git',
        'source': 'https://github.com/adorsk-noaa/georefine.git',
        'path': 'georefine',
    },

    'sa_dao' : {
        'type': 'git',
        'source': 'https://github.com/adorsk-noaa/sqlalchemy_dao.git',
        'path': 'lib/sa_dao'
    },

    'georefine_client' : {
        'type': 'git',
        'source': 'https://github.com/adorsk-noaa/grc2.git',
    },

    'task_manager' : {
        'type': 'git',
        'source': 'https://github.com/adorsk/TaskManager.git',
        'path': 'lib/task_manager',
    },
}
