import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    # Common
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # For Flask-SqlAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False