import logging
from sys import stdout


class Logger:

    def __init__(self):
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self._get_console_handler())

    def _get_console_handler(self):
        """ Returns console handler which outputs to stdout with log level of info

        :return: stdout StreamHandler
        """
        console_handler = logging.StreamHandler(stdout)
        return console_handler

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger
