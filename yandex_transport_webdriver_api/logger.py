"""
This is a logger module, to simplify logging to the screen.
Logs messages are printed in the following format:

   LOG LEVEL : [ Timestamp ] : Message

Log levels include NONE, ERROR, WARNING, INFO and DEBUG.
No log messages above current verbose level will be printed.

"""

import sys
import datetime


class Logger:
    """
    Logger class, handles printing log messages based on set verbosity level.
    """
    # Logging levels
    NONE = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4

    _verbose = ERROR
    @property
    def verbose(self):
        """Current verbosity level of the program"""
        return self._verbose

    @verbose.setter
    def verbose(self, value):
        """Set current verbosity level of the program
        :param value: desired verbosity level: NONE, ERROR, WARNING, INFO, DEBUG
        :return: nothing
        """
        if value > self.DEBUG:
            value = self.DEBUG
        if value < self.NONE:
            value = self.NONE
        self._verbose = value

    def __init__(self, log_level):
        self.verbose = log_level

    def log(self, log_level, text):
        """
        Log data to stderr
        :param log_level: log level, see Application.LOG_SOMETHING constants.
        :param text: text to print
        :return: nothing
        """
        timestamp = '['+str(datetime.datetime.now())+']'
        if log_level == self.ERROR:
            if self.verbose >= self.ERROR:
                print("ERROR :", timestamp, ":", str(text), file=sys.stderr)
                return

        if log_level == self.WARNING:
            if self.verbose >= self.WARNING:
                print("WARN  :", timestamp, ":", str(text), file=sys.stderr)
                return

        if log_level == self.INFO:
            if self.verbose >= self.INFO:
                print("INFO  :", timestamp, ":", str(text), file=sys.stderr)
                return

        if log_level == self.DEBUG:
            if self.verbose >= self.DEBUG:
                print("DEBUG :", timestamp, ":", str(text), file=sys.stderr)
                return

    def error(self, text):
        """
        Log error message
        :param text: text to print
        :return: nothing
        """
        self.log(self.ERROR, text)

    def warning(self, text):
        """
                Log warning message
                :param text: text to print
                :return: nothing
                """
        self.log(self.WARNING, text)

    def info(self, text):
        """
                Log info message
                :param text: text to print
                :return: nothing
                """
        self.log(self.INFO, text)

    def debug(self, text):
        """
                Log debug message
                :param text: text to print
                :return: nothing
                """
        self.log(self.DEBUG, text)
