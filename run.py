"""
Main entry point for the Employee Monitoring System
"""
import sys
import logging
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app import app, socketio, config

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    logger.info("=" * 60)
    logger.info("Employee Monitoring System")
    logger.info("=" * 60)
    logger.info(f"Starting server on {config.HOST}:{config.PORT}")
    logger.info(f"Detection Model: {config.DETECTION_MODEL}")
    logger.info(f"Absence Timeout: {config.ABSENCE_TIMEOUT_MINUTES} minutes")
    logger.info(f"Database: {config.DATABASE_PATH}")
    logger.info("=" * 60)
    
    try:
        # Run the Flask-SocketIO server
        socketio.run(
            app,
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
