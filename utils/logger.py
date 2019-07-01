import logging


class Logger:
    def __init__(self, logger_name=None, fmt=None, filename=None, filemode="a", stream_level=logging.INFO, file_level=logging.DEBUG):
        """
        Create a Logger class. This is a wrapper for the logging library.

        :param logger_name: The name of the Logger module.
        :param fmt: The format to use for the Logger class.
        :param filename: The filename to use if logging to file.
        """
        if not logger_name:
            logger_name = __name__

        # Setup the main logging facilities.
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        fmt = logging.Formatter(fmt if fmt else "[%(asctime)s - %(levelname)s]: %(message)s")

        # Setup the handlers.
        console_handler = logging.StreamHandler()
        console_handler.setLevel(stream_level)
        console_handler.setFormatter(fmt)

        if filename:
            file_handler = logging.FileHandler(filename, filemode)
            file_handler.setLevel(file_level)
            file_handler.setFormatter(fmt)

            self.logger.addHandler(file_handler)

        self.logger.addHandler(console_handler)

    def debug(self, message):
        self.log(logging.DEBUG, message)

    def info(self, message):
        self.log(logging.INFO, message)

    def warn(self, message):
        self.log(logging.WARN, message)

    def err(self, message):
        self.log(logging.ERROR, message)

    def fatal(self, message):
        self.log(logging.FATAL, message)

    def log(self, level, message):
        """
        The main logging function. The other wrapper functions will call this with different log levels.

        :param level: The logging level.
        :param message: The message to log.
        :return: Nothing.
        """

        self.logger.log(level, message)
