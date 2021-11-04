import logging
import os
import sys
from colorama import Fore, Style

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


class Formatter(logging.Formatter):

    def __init__(self, fmt=None):
        if fmt is None:
            fmt = self._colorized_fmt()
        logging.Formatter.__init__(self, fmt)

    def _colorized_fmt(self, color=Fore.RESET):
        return f'{color}[%(asctime)s] %(levelname)s: %(message)s{Style.RESET_ALL}'

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            color = Fore.CYAN
        elif record.levelno == logging.INFO:
            color = Fore.GREEN
        elif record.levelno == logging.WARNING:
            color = Fore.YELLOW
        elif record.levelno == logging.ERROR:
            color = Fore.RED
        elif record.levelno == logging.CRITICAL:
            color = Fore.MAGENTA
        else:
            color = Fore.WHITE
        self._style._fmt = self._colorized_fmt(color)

        # Call the original formatter class to do the grunt work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


class Logger(logging.Logger):

    def __init__(self, log_file_name=None):
        super().__init__('fngs')

        logging_formatter = Formatter()

        if log_file_name is not None:
            self.file_handler = logging.FileHandler(os.path.join(SCRIPT_DIRECTORY, log_file_name))
            self.file_handler.setFormatter(logging_formatter)
            self.file_handler.setLevel(logging.DEBUG)
            self.addHandler(self.file_handler)

        self.console_handler = logging.StreamHandler(sys.stderr)
        self.console_handler.setFormatter(logging_formatter)
        self.console_handler.setLevel(logging.INFO)
        self.addHandler(self.console_handler)

        logging.getLogger('requests').setLevel(logging.WARNING)


logger = None
