"""PAskit - AI-powered interactive teaching software.

Main application entry point.
"""

import sys
import asyncio
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import qasync

from src.core.config import Config
from src.core.logger import setup_logger
from src.core.events import get_event_bus
from loguru import logger


def main():
    """Main application entry point."""
    try:
        # Load configuration
        config = Config.load()

        # Setup logging
        setup_logger(log_level=config.log_level, log_to_file=config.log_to_file)
        logger.info("Starting PAskit application")

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("PAskit")
        app.setOrganizationName("PAskit")

        # Initialize event bus
        event_bus = get_event_bus()
        logger.info("Event bus initialized")

        # Setup qasync event loop
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)
        logger.info("Async event loop initialized")

        # Import and create main window (delayed import to ensure config is loaded)
        from src.gui.main_window import MainWindow

        logger.info("Creating MainWindow...")
        main_window = MainWindow(config, event_bus)
        logger.info("MainWindow created successfully")

        logger.info("Showing MainWindow...")
        main_window.show()
        logger.info("MainWindow.show() completed")

        logger.info("Application started successfully")

        # Start event loop with qasync
        logger.info("Starting event loop...")
        with loop:
            logger.info("Inside event loop context")
            return loop.run_forever()

    except Exception as e:
        logger.exception(f"Fatal error during application startup: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
