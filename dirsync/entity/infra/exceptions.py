class InvalidConfigIntervalError(Exception):
    '''Raised when the interval_ms passed to the Config constructor is invalid.'''
    pass

class InvalidRepositoryLocationError(Exception):
    '''Raised when a RepositoryFactory generator method cannot infer the repository type.'''
    pass

class LogfileInRepoError(Exception):
    '''Raised when the user-provided logfile path is in the repo (currently unsupported, breaks change tracking).'''
    pass

class DestinationRepoNotEmptyError(Exception):
    '''Raised when the destination repository is not empty.'''
    pass