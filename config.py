import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///travel_planner.db'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
