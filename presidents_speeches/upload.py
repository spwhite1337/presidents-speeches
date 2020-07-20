import os
import re
import argparse
from config import Config, logger


def upload():
    parser = argparse.ArgumentParser(prog='Upload card classifier')
    parser.add_argument('--windows', action='store_true')
    parser.add_argument('--skipdata', action='store_true')
    parser.add_argument('--skipresults', action='store_true')
    parser.add_argument('--dryrun', action='store_true')
    args = parser.parse_args()

    # General commands
    sync_base = 'aws s3 sync '
    dryrun_arg = ' --dryrun'
    results_sync = '{} {}'.format(Config.RESULTS_DIR, Config.CLOUD_RESULTS)
    data_sync = '{} {}'.format(Config.DATA_DIR, Config.CLOUD_DATA)

    include_flag = " --exclude '*/.gitignore'"
    if args.windows:
        include_flag = re.sub("'", "", include_flag)

    if not args.skipdata:
        logger.info('Uploading Data')
        ps_sync = sync_base + data_sync + include_flag
        ps_sync += dryrun_arg if args.dryrun else ''
        logger.info(ps_sync)
        os.system(ps_sync)
    if not args.skipresults:
        logger.info('Uploading Results')
        ps_sync = sync_base + results_sync + include_flag
        ps_sync += dryrun_arg if args.dryrun else ''
        logger.info(ps_sync)
        os.system(ps_sync)
