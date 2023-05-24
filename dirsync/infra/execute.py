import logging
from time import sleep

from dirsync.entity.core.repository.repository import Repository
from dirsync.entity.infra.config import Config


def execute(src_repo: Repository, dest_repo: Repository, config: Config):
    '''Executes main program loop..'''
    while True:
        # check source repository for changes
        src_changes = src_repo.update_status()

        # parse and sync changes from src_repo to dest_repo
        for change in src_changes:
            logging.debug(change)

            change_parts = change.split(' ')
            command = change_parts[0]
            file_hash = change_parts[1]
            file_loc = change_parts[3]

            if command == 'create':
                dest_repo.create_file(file_loc, src_repo.get_file_at_path(file_loc).read())
            elif command == 'modify':
                dest_repo.modify_file(file_loc, src_repo.get_file_at_path(file_loc).read())
            elif command == 'move':
                dest_repo.move_file(file_hash, file_loc)
            elif command == 'copy':
                dest_repo.copy_file(file_hash, file_loc)
            elif command == 'delete':
                dest_repo.delete_file(file_loc)

        # prune empty dirs and files not in src_repo from dest_repo
        dest_repo.prune()

        # restore any changes made to files in dest_repo
        dest_changes = dest_repo.update_status()
        for change in dest_changes:
            change_parts = change.split(' ')
            command = change_parts[0]
            file_loc = change_parts[3]

            if command == 'modify':
                logging.debug(f'restore {src_repo.get_file_at_path(file_loc).last_hash} -> {file_loc}')
                dest_repo.modify_file(file_loc, src_repo.get_file_at_path(file_loc).read())

        # wait for given interval
        sleep(config.interval_ms / 1000)
