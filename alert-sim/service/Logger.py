from .LoggingFormatter import LoggingFormatter
import logging
logger = logging.getLogger("Sim")
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(LoggingFormatter())
logger.addHandler(ch)

class Logger:
    def getLogger():
        return logger
