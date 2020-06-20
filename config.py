import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
SCHEME = 'postgresql'
DATABASE_NAME = "fyyur"
USER = "fyyuruser"
PASSWORD = "fyyurpass123"
HOST = "localhost"
PORT = 5432

SQLALCHEMY_DATABASE_URI = f'{SCHEME}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False