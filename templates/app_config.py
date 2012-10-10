""" Flask config. """

SECRET_KEY = "thesecretkey"

#SERVER_NAME = "theservername"

APPLICATION_ROOT = "/georefine"

#@TODO: GET THIS FROM NODE DATA, stored outside of public version control.
SQLALCHEMY_DATABASE_URI = "postgresql://georefine:georefine@localhost/georefine"

STATIC_DIR = "/home/georefine/public"

PROJECT_STATIC_DIR_NAME = "public"

PROJECT_STATIC_URL = lambda p: "/static/project_%s/public" % p.id




