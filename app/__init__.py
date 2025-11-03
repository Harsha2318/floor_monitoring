"""
Employee Monitoring System - Application Package
"""

__version__ = '1.0.0'
__author__ = 'Floor Monitoring System'

from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
from pathlib import Path

from app import config

# Initialize Flask app
app = Flask(__name__,
            template_folder=str(config.BASE_DIR / 'templates'),
            static_folder=str(config.BASE_DIR / 'static'))

app.config.from_object(config)

# Initialize extensions
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info(f"Employee Monitoring System v{__version__} initialized")
