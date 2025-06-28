import logging
from os import environ

# Logging levels
logging_levels = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}


class ColorFormatter(logging.Formatter):
    COLORS = {
        'WARNING': '\033[93m',   # Yellow
        'ERROR': '\033[91m',     # Red
        'CRITICAL': '\033[95m',  # Magenta
        'DEBUG': '\033[94m',     # Blue
        'INFO': '\033[92m',      # Green
        'RESET': '\033[0m'       # Reset color
    }

    def format(self, record):
        import json
        log_format_string = json.dumps({
            'logLevel': '%(levelname)s',
            'time': '%(asctime)s',
            'line': "%(filename)s: %(lineno)d",
            'message': '%(message)s',
        }, indent=None)
        log_message = logging.Formatter(log_format_string).format(record)
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        return f"{color}{log_message}{reset}"


def set_logging_config(log_level: str, log_file: str = None, only_logs: bool = False):
    # Logs formatter
    stream_formatter = ColorFormatter(
        "\n%(asctime)s [File: %(filename)s:%(lineno)d] \t[Module: %(module)s]\t %(levelname)s: %(message)s"
    )
    log_file_formatter = ColorFormatter(
        '{"timestamp": "%(asctime)s", "filename": "%(filename)s:%(lineno)d", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}'
    )

    # Where to put logs
    logging_handlers = []

    # Include stdout by default, if only_logs is set the log format is JSON
    stream_handler = logging.StreamHandler()
    if only_logs:
        stream_handler.setFormatter(log_file_formatter)
    else:
        stream_handler.setFormatter(stream_formatter)
    logging_handlers.append(stream_handler)

    # Log to file configuration
    if log_file:
        # Set log to file handler
        log_file_handler = logging.FileHandler(log_file)
        log_file_handler.setFormatter(log_file_formatter)
        # Append the log formatter
        logging_handlers.append(log_file_handler)

    # Set Log Level, environment takes precedence over the --log-level argument
    try:
        log_level = environ["LOG_LEVEL"]
    except KeyError:
        log_level = log_level

    # Configure Logger
    # Initialize you log configuration using the base class
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    logging.basicConfig(
        level=logging_levels.get(log_level),
        handlers=logging_handlers,
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )


# Retrieve the logger instance
logger = logging.getLogger()
