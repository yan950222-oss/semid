import os

class Config:
    # Secret key for session management. Use a random value in production.
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    # SQLite database file in the project directory
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASEDIR, 'app.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
