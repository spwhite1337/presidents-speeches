import os
from config import Config, logger


def upload():
    logger.info('Uploading Data')
    os.system('aws s3 sync {} {}'.format(Config.DATA_DIR, Config.CLOUD_DATA))
    logger.info('Uploading Results')
    os.system('aws s3 sync {} {}'.format(Config.RESULTS_DIR, Config.CLOUD_RESULTS))
