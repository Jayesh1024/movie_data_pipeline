import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler=logging.FileHandler('run.log')
formatter=logging.Formatter(fmt="%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(lineno)d:%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)