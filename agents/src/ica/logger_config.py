import logging

class LoggerConfig:
    @staticmethod
    def setup_logger(name: str, log_file: str = "agent_47_app.log", level=logging.DEBUG):
        """Configures and returns a logger instance."""
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Prevent duplicate handlers
        if logger.hasHandlers():
            return logger

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # File handler (logs all levels)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger
