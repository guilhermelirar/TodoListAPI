import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'very_secure_key'
