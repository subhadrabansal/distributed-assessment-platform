import os
import secrets

class Config:
    SECRET_KEY = secrets.token_hex(16)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///distributed-assessment-platform.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY= SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    IITM_EMAIL_USER = os.environ.get('IITM_EMAIL_USER')
    IITM_EMAIL_PASS = os.environ.get('IITM_EMAIL_PASS')
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('IITM_EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('IITM_EMAIL_PASS')
    MAIL_DEFAULT_SENDER = os.environ.get('IITM_EMAIL_USER')
