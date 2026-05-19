import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    if not os.path.exists('log'):
        os.makedirs('log')
    log_file = 'log/app.log'
    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG) 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    if app.debug: 
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG) 
