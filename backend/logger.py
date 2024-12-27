"""
Custom logger class using python logging library
"""
import os
import logging
from logging.handlers import TimedRotatingFileHandler
import logging.config

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')


class Logger:
    """
    Serves as a wrapper for logger class of logging library
    """

    def __init__(self, name: str, log_level: str = 'INFO'):
        """
        Args:
            name:           name of the logger (str)
            path_logs:      path to logs directory (str)
            log_level:      logging level (int)

            Uses log levels according to logging library:
            DEBUG -> INFO -> WARNING -> ERROR -> CRITICAL
        """
        self._path_log = f"{LOGS_DIR}/log.log"
        self._name = name

        match log_level:
            case ('DEBUG'):
                self._log_level = logging.DEBUG
            case ('INFO'):
                self._log_level = logging.INFO
            case ('WARNING'):
                self._log_level = logging.WARNING
            case ('ERROR'):
                self._log_level = logging.ERROR
            case ('CRITICAL'):
                self._log_level = logging.CRITICAL
            case _:
                self._log_level = logging.INFO

    def get_main_logger(self):
        """
        Creates a main logger that formats and writes the logs
        Only one main logger should exist at a time

        Returns:
            Main logger object
        """
        # get logger
        logger = logging.getLogger(f"{self._name}")
        logger.setLevel(self._log_level)

        # EXAMPLE: [2024-09-05 14:10:12,708] [         server_logger] [ INFO] [132] - [SERVER]    [GET] root
        log_format = '[%(asctime)s] [%(name)20s] [%(levelname)5s] [%(lineno)3d] %(message)s'
        formatter = logging.Formatter(
            log_format
        )
        stream_handler = TimedRotatingFileHandler(self._path_log, when='midnight', interval=1, backupCount=3)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        return logger

    def get_child_logger(self):
        """
        Creates a module logger

        Returns:
            Child logger object
        """
        logger = logging.getLogger(f"{self._name}")
        logger.setLevel(self._log_level)

        return logger
