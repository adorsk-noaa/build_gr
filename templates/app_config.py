""" Flask config. """

SECRET_KEY = "thesecretkey"

#SERVER_NAME = "theservername"

APPLICATION_ROOT = "georefine"

#@TODO: GET THIS FROM NODE DATA, stored outside of public version control.
SQLALCHEMY_DATABASE_URI = "postgresql://georefine:georefine@localhost/georefine"

STATIC_FOLDER = "/home/georefine/public"

STATIC_URL_PATH = "/static"

GRC_USE_MINIFIED = True
