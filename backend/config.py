# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI ='postgresql://postgres:10242048@localhost:5432'
    # 'postgresql://your_user:your_password@localhost/your_database'
