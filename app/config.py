import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_secure_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///todo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
