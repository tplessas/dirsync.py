import hashlib

from dirsync.entity.core.file.file import File

class LocalFile(File):
    '''
    Represents a file in a LocalDirectoryRepository.

    Attributes
    ----------
    abs_path : str
        absolute path of file in filesystem
    rel_path : str
        relative path of file with respect to repository root
    last_hash : str
        hash of file before last edit/deletion

    Methods
    -------
    calculate_blake2b_hash() -> str:
        Calculates the BLAKE2b hash of the file and sets the object's `last_hash` attribute.
    '''

    def __init__(self,
                 abs_path: str,
                 rel_path: str):
        self.abs_path: str = abs_path
        self.rel_path: str = rel_path
        self.last_hash: str = None
        self.calculate_blake2b_hash()

    def calculate_blake2b_hash(self) -> str:
        '''
        Calculates the BLAKE2b hash of the file and sets the object's `last_hash` attribute.

        Returns:
            hash (str): the BLAKE2b hash of the file
        '''
        hasher = hashlib.blake2b()
        with open(self.abs_path, "rb") as file:
            for chunk in iter(lambda: file.read(4096), b""):
                hasher.update(chunk)

        self.last_hash = hasher.hexdigest()
        return self.last_hash