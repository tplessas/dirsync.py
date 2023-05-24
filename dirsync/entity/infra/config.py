from dataclasses import dataclass

from dirsync.entity.infra.exceptions import InvalidConfigIntervalError

@dataclass(frozen=True)
class Config:
    '''
    Container/validator for basic application config values.

    Attributes
    ----------
    src_dir : str
        source directory to be synced
    dest_dir : str
        destination/replica directory
    logfile_path : str
        path where the src_dir changelog will be written
    interval_ms : int
        frequency of execution of sync task in milliseconds
    '''
    src_dir: str
    dest_dir: str
    logfile_path: str
    interval_ms: int

    def __post_init__(self):
        if self.interval_ms < 1:
            raise InvalidConfigIntervalError()
