import logging
import sys

from dirsync.entity.core.repository.repositoryfactory import RepositoryFactory
from dirsync.entity.infra.config import Config

from dirsync.infra.execute import execute
from dirsync.entity.infra import exceptions as exc


def bootstrap_app(config: Config):
    '''Initialize app infrastructure and call executor.'''
    # configure logger
    logging.basicConfig(format='[%(levelname)s|%(asctime)s]: %(message)s',
                        level=logging.DEBUG,
                        handlers=[
                            logging.FileHandler(config.logfile_path),
                            logging.StreamHandler(sys.stdout)
                        ])

    # create repository objects pointing to user-provided locations
    try:
        src_repo = RepositoryFactory.generate_repository(config.src_dir, config)
    except exc.InvalidRepositoryLocationError:
        exit('dirsync.py: error: could not register src_repo')
    except exc.LogfileInRepoError:
        exit('dirsync.py: error: logfile inside src_repo currently unsupported')

    try:
        dest_repo = RepositoryFactory.generate_repository(config.dest_dir, config)
    except exc.InvalidRepositoryLocationError:
        exit('dirsync.py: error: could not register dest_repo')
    except exc.LogfileInRepoError:
        exit('dirsync.py: error: logfile inside dest_repo will be overwritten on sync')
    except exc.DestinationRepoNotEmptyError:
        exit('dirsync.py: error: dest_repo is not empty')

    # run app
    execute(src_repo, dest_repo, config)
