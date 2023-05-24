import argparse

from dirsync.entity.infra import exceptions as exc
from dirsync.entity.infra.config import Config
from dirsync.infra.bootstrap import bootstrap_app

def execute():
    '''Reads in CLI arguments and passes a Config to the bootstrapper.'''
    argparser = argparse.ArgumentParser(
        prog='dirsync.py',
        description='A Python tool to maintain an up-to-date replica of a repository.'
    )

    argparser.add_argument(
        'src_dir',
        help='source repository to be synced',
        type=str
    )

    argparser.add_argument(
        'dest_dir',
        help='destination/replica repository',
        type=str
    )

    argparser.add_argument(
        'logfile_path',
        help='path where the sync logfile will be written',
        type=str
    )

    argparser.add_argument(
        'interval_ms',
        help='frequency of execution of sync task in milliseconds',
        type=int
    )

    # cast to Config object to run validator logic
    try:
        config = Config(**vars(argparser.parse_args()))
    except exc.InvalidConfigIntervalError:
        exit('usage: dirsync.py [-h] src_dir dest_dir logfile_path interval_ms\n' \
             'dirsync.py: error: interval_ms must be >= 1')

    bootstrap_app(config)
