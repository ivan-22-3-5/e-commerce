import logging
from sys import stdout

logger = logging.getLogger("main_logger")
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stdout)
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

logger.addHandler(handler)
