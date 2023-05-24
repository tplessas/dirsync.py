from abc import ABC, abstractmethod

from dirsync.entity.core.file.file import File

class Repository(ABC):
    '''Abstract repository class.'''

    @abstractmethod
    def update_status(self) -> list[str]:
        pass

    @abstractmethod
    def get_file_at_path(self, rel_path: str) -> File:
        pass

    @abstractmethod
    def get_file_with_hash(self, file_hash: str) -> File:
        pass

    @abstractmethod
    def create_file(self, rel_path: str, content: bytes) -> None:
        pass

    @abstractmethod
    def modify_file(self, rel_path: str, content: bytes) -> None:
        pass

    @abstractmethod
    def move_file(self, src_hash: str, dest_rel_path: str) -> None:
        pass

    @abstractmethod
    def copy_file(self, src_hash: str, dest_rel_path: str) -> None:
        pass

    @abstractmethod
    def delete_file(self, rel_path: str) -> None:
        pass

    @abstractmethod
    def prune(self) -> None:
        pass
