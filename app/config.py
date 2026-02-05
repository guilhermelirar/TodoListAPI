import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_secure_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///todo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET') or 'acc_token_secret'
    REFRESH_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET') or 'rfs_token_secret'

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
