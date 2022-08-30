from .LoggingFormatter import LoggingFormatter
import logging

class Logger:
    def getLogger(name: str, level: int = logging.INFO):
        logger = logging.getLogger(name)
        logger.setLevel(level)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(LoggingFormatter())
        logger.addHandler(ch)
        return logger
