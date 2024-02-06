import os

# Get the base directory of this folder
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Example for PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')#'postgresql://postgres:Minnie4511!@localhost:5432/yoga_retreat'
    FLASK_DEBUG =os.environ.get('FLASK_DEBUG')     #1
    BOOKRETREATS_API_URL =os.environ.get('BOOKRETREATS_API_URL')     #'https://api.bookretreats.com/'