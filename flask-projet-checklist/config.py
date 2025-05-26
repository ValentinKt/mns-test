import os
from pathlib import Path

basedir = Path(__file__).parent

class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    SECRET_KEY = os.urandom(24)
    # os.environ.get('DATABASE_URL') or \
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'instance', 'checklist.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
