import os
from decouple import config

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = config('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:lzQ432amnKA@localhost/your_assistant'
    # or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
