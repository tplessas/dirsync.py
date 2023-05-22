from enum import Enum
import os

from dirsync.entity.core.repository.repository import Repository
from dirsync.entity.core.repository.local.localdirrepo import LocalDirectoryRepository

from dirsync.entity.infra.config import Config
from dirsync.entity.infra.exceptions import InvalidRepositoryLocationError


class RepositoryType(Enum):
    '''Represents the type of repository requested in RepositoryFactory methods.'''
    LOCALDIR = 1

class RepositoryFactory:
    '''Host class for repository generation methods.'''
    @staticmethod
    def generate_repository(location: str, config: Config, type: RepositoryType = None) -> Repository:
        '''
        Basic repository factory method.

        Parameters:
            location (str): string representation of location of repository (path, ftp server, etc.),
                repository type inferred from it
            config (Config): user program configuration
            type (RepositoryType): requested type of repository,
                overrides any inferred from `location`
        
        Returns:
        repository : Repository
            a concrete object of a subtype of Repository
        '''
        if type == RepositoryType.LOCALDIR:
            return LocalDirectoryRepository(location, config)

        if os.path.exists(os.path.dirname(location)):
            return LocalDirectoryRepository(location, config)

        raise InvalidRepositoryLocationError()