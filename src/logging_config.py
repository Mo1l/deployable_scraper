# src/logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO') # defaults to INFO when not set
    
    # Single continuous log file with rotation
    file_handler = RotatingFileHandler(
        './data/logs/scraper.log',  # Same filename always
        maxBytes=50*1024*1024,      # 50MB
        backupCount=2               # Keeps scraper.log.1, .2, .3, .4, .5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        handlers=[console_handler, file_handler],
        force=True
    )