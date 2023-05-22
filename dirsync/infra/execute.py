import logging
from time import sleep

from dirsync.entity.core.repository.repository import Repository
from dirsync.entity.infra.config import Config


def execute(src_repo: Repository, dest_repo: Repository, config: Config):
    '''Executes main program loop..'''
    while(True):
        # check source repository for changes
        changes = src_repo.update_status()

        # log changes
        for change in changes:
            logging.debug(change)

        # wait for given interval
        sleep(config.interval_ms / 1000)