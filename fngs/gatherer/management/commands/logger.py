import logging
import os
import sys

SCRIPT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)


def init_logger(debug: bool):
    global logger
    logger.setLevel(logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.WARNING)

    logging_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')

    # TODO: Replace with TimedRotatingFileHandler
    file_handler = logging.FileHandler(os.path.join(SCRIPT_DIRECTORY,
                                                    'gatherfromsources.log'))
    file_handler.setFormatter(logging_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(logging_formatter)
    console_handler.setLevel(logging.INFO if not debug else logging.DEBUG)
    logger.addHandler(console_handler)
