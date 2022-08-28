import logging

class LoggingFormatter(logging.Formatter):

    grey = "\033[37m"
    green = "\033[32m"
    yellow = "\033[93m"
    red = "\033[31m"
    bold_red = "\033[31;1m"
    reset = "\033[0m"
    format = "[%(asctime)s - %(name)s - %(levelname)s] %(message)s"
    filename = "(%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + filename  + reset,
        logging.CRITICAL: bold_red + format + filename + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
