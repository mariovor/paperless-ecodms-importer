import logging


class MigrationLogger:
    LOGGER = None
    @classmethod
    def get_logger(cls):
        logger = None
        if cls.LOGGER is None:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            # Create a console handler
            console_handler = logging.StreamHandler()  # Create a formatter that includes date, time, and log level
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            # Set the formatter for the console handler
            console_handler.setFormatter(formatter)
            # Add the handler to the logger
            logger.addHandler(console_handler)
            cls.LOGGER = logger
            return logger
        else:
            return cls.LOGGER

