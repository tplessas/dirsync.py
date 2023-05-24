from enum import Enum
import os
import shutil

from dirsync.entity.core.file.local.localfile import LocalFile
from dirsync.entity.core.repository.repository import Repository

from dirsync.entity.infra.config import Config
from dirsync.entity.infra.exceptions import LogfileInRepoError, DestinationRepoNotEmptyError

class LocalDirectoryRepositoryState(Enum):
    '''Represents last action taken in LocalDirectoryRepository objects.'''
    INIT = 1
    READ = 2
    CREATE = 3
    MODIFY = 4
    MOVE = 5
    COPY = 6
    DELETE = 7
    PRUNE = 8
    GET = 9

class LocalDirectoryRepository(Repository):
    '''
    Represents state of local directory.

    Attributes
    ----------
    path : str
        path of directory in filesystem
    last_action : LocalDirectoryRepositoryState
        last action executed in repository
    filepath_file_map : dict[str, LocalFile]
        maps file paths from directory root to LocalFile objects
    hash_file_map : dict[str, list[LocalFile]]
        maps hashes of files in directory to LocalFile objects

    Methods
    -------
    update_status() -> list[str]:
        Updates the state of the object by scanning the directory for changes.
    _contains(path: str) -> bool:
        Returns whether the given file is part of the directory tree.
    get_file_at_path(rel_path: str) -> LocalFile:
       Returns a LocalFile object found using its relative path.
    get_file_with_hash(file_hash: str) -> LocalFile:
       Returns a LocalFile object found using its hash.
    create_file(rel_path: str, content: bytes) -> None:
        Creates a new repository file at a relative path storing contents provided as a `bytes` object.
    modify_file(rel_path: str, content: bytes) -> None:
        Replaces the contents of a repository file at a relative path with the provided `bytes` content.
    move_file(src_hash: str, dest_rel_path: str) -> None:
        Moves a file already existing in the repository to another location.
    copy_file(src_hash: str, dest_rel_path: str) -> None:
        Copies a file already existing in the repository to another location.
    delete_file(rel_path: str) -> None:
        Deletes an existing repository file at a relative path.
    prune() -> None:
        Recursively removes any empty directories inside the repository,
        as well as files not in its state.
    '''

    def __init__(self,
                 path: str,
                 config: Config):
        self.path = os.path.abspath(path)

        if self._contains(config.logfile_path):
            raise LogfileInRepoError()
        if self.path == os.path.abspath(config.dest_dir) and os.listdir(self.path):
            raise DestinationRepoNotEmptyError()

        self.filepath_file_map: dict[str, LocalFile] = {}
        self.hash_file_map: dict[str, list[LocalFile]] = {}

        self.last_action: LocalDirectoryRepositoryState = LocalDirectoryRepositoryState.INIT

    def update_status(self) -> list[str]:
        '''
        Updates the state of the object by scanning the directory for changes. Considers all
        `copy` operations as `create` ones when the object's `state` attribute is INIT,
        since a file might already be duplicated in the repository before the first execution.
        
        Returns
        -------
        new_changes : list[str]
            log of all changes since last execution
        '''

        new_changes: list[str] = []
        # walk directory and all subdirectories to get file paths
        abs_file_paths = []
        for dirpath, _, filenames in os.walk(self.path):
            for filename in filenames:
                abs_file_paths.append(os.path.join(dirpath, filename))

        # create entries and log changes for new files
        moved_file_hashes = []
        for abs_file_path in abs_file_paths:
            rel_file_path = abs_file_path[len(self.path) + 1:]
            if rel_file_path not in self.filepath_file_map:
                new_file = LocalFile(abs_file_path, rel_file_path)
                self.filepath_file_map[rel_file_path] = new_file

                # check whether file has been moved/copied using hash
                if new_file.last_hash in self.hash_file_map:
                    # try to find at least one version of file still in directory tree
                    file_copied = False
                    for original_file in self.hash_file_map[new_file.last_hash]:
                        if os.path.isfile(original_file.abs_path): # one original file still exists (copied)
                            # consider all files created the first time this method runs
                            if self.last_action == LocalDirectoryRepositoryState.INIT:
                                new_changes.append(f'create {new_file.last_hash} -> {new_file.rel_path}')
                            else:
                                new_changes.append(f'copy {new_file.last_hash} -> {new_file.rel_path}')
                            self.hash_file_map[new_file.last_hash].append(new_file)
                            file_copied = True
                            break
                    if not file_copied: # no original file exists anymore (moved)
                        new_changes.append(f'move {new_file.last_hash} -> {new_file.rel_path}')
                        moved_file_hashes.append(new_file.last_hash)
                        self.hash_file_map[new_file.last_hash].append(new_file)
                else: # file not copied/moved (create)
                    self.hash_file_map[new_file.last_hash] = [new_file]
                    new_changes.append(f'create {new_file.last_hash} -> {new_file.rel_path}')
            else: # check and log if file has been modified using hash
                file = self.filepath_file_map[rel_file_path]
                file_last_hash = file.last_hash
                file_new_hash = file.calculate_blake2b_hash()
                if file_last_hash != file_new_hash:
                    self.hash_file_map[file_last_hash].remove(file)
                    # check if another file was copied and renamed to original
                    if file_new_hash not in self.hash_file_map:
                        self.hash_file_map[file_new_hash] = [file]
                        new_changes.append(f'modify {file_new_hash} -> {file.rel_path}')
                    else:
                        self.hash_file_map[file_new_hash].append(file)
                        new_changes.append(f'copy {file_new_hash} -> {file.rel_path}')

        # prune deleted files from maps
        for rel_file_path, file in self.filepath_file_map.copy().items():
            if not os.path.isfile(file.abs_path):
                del self.filepath_file_map[rel_file_path]
                self.hash_file_map[file.last_hash].remove(file)
                # moving deletes original, operation already logged
                if file.last_hash not in moved_file_hashes:
                    new_changes.append(f'delete {file.last_hash} -> {rel_file_path}')
        
        self.last_action = LocalDirectoryRepositoryState.READ
        return new_changes

    def get_file_at_path(self, rel_path: str) -> LocalFile:
        '''Returns a LocalFile object found using its relative path.'''

        self.last_action = LocalDirectoryRepositoryState.GET
        return self.filepath_file_map[rel_path]

    def get_file_with_hash(self, file_hash: str) -> LocalFile:
        '''Returns a LocalFile object found using its hash.'''

        self.last_action = LocalDirectoryRepositoryState.GET
        return self.hash_file_map[file_hash]

    def create_file(self, rel_path: str, content: bytes) -> None:
        '''Creates a new repository file at a relative path storing contents provided as a `bytes` object.'''

        abs_path = self.path + os.sep + rel_path

        # create path if needed
        dirpath = os.sep.join(abs_path.split(os.sep)[:-1])
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        # write file
        with open(abs_path, 'wb') as file:
            file.write(content)

        # add file refernce to repository state
        file_obj = LocalFile(abs_path, rel_path)
        self.filepath_file_map[rel_path] = file_obj
        self.hash_file_map[file_obj.last_hash] = [file_obj]

        self.last_action = LocalDirectoryRepositoryState.CREATE

    def modify_file(self, rel_path: str, content: bytes) -> None:
        '''Replaces the contents of a repository file at a relative path with the provided `bytes` content.'''

        file_obj = self.filepath_file_map[rel_path]
        old_hash = file_obj.last_hash

        abs_path = self.path + os.sep + rel_path
        with open(abs_path, 'wb') as file:
            file.write(content)

        # replace in map with new hash
        self.hash_file_map[old_hash].remove(file_obj)
        new_hash = file_obj.calculate_blake2b_hash()
        self.hash_file_map[new_hash] = [file_obj]

        self.last_action = LocalDirectoryRepositoryState.MODIFY

    def move_file(self, src_hash: str, dest_rel_path: str) -> None:
        '''Moves a file already existing in the repository to another location.'''

        file_obj = self.hash_file_map[src_hash][0]
        src_abs_path = file_obj.abs_path
        dest_abs_path = self.path + os.sep + dest_rel_path

        # create path if needed
        dirpath = os.sep.join(dest_abs_path.split(os.sep)[:-1])
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        # move file
        shutil.move(src_abs_path, dest_abs_path)

        # update file object and filepath map
        file_obj.abs_path = dest_abs_path
        src_rel_path = file_obj.rel_path
        file_obj.rel_path = dest_rel_path
        del self.filepath_file_map[src_rel_path]
        self.filepath_file_map[dest_rel_path] = file_obj

        self.last_action = LocalDirectoryRepositoryState.MOVE

    def copy_file(self, src_hash: str, dest_rel_path: str) -> None:
        '''Copies a file already existing in the repository to another location.'''

        src_file_obj = self.hash_file_map[src_hash][0]
        src_abs_path = src_file_obj.abs_path
        dest_abs_path = self.path + os.sep + dest_rel_path

        # create path if needed
        dirpath = os.sep.join(dest_abs_path.split(os.sep)[:-1])
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        # copy file
        shutil.copy(src_abs_path, dest_abs_path)

        # create new file object
        dest_file_obj = LocalFile(dest_abs_path, dest_rel_path)
        self.filepath_file_map[dest_rel_path] = dest_file_obj
        self.hash_file_map[dest_file_obj.last_hash].append(dest_file_obj)

        self.last_action = LocalDirectoryRepositoryState.COPY

    def delete_file(self, rel_path: str) -> None:
        '''Deletes an existing repository file at a relative path.'''

        file_obj = self.filepath_file_map[rel_path]
        abs_path = self.filepath_file_map[rel_path].abs_path
        file_hash = file_obj.last_hash

        # delete file
        os.remove(abs_path)

        # remove references to file
        del self.filepath_file_map[rel_path]
        self.hash_file_map[file_hash].remove(file_obj)

        self.last_action = LocalDirectoryRepositoryState.DELETE

    def prune(self) -> None:
        '''
        Recursively removes any empty directories inside the repository,
        as well as files not in its state.
        '''
        # delete empty directories
        for dirpath, subdirs, filenames in os.walk(self.path, topdown=False):
            if not subdirs and not filenames and dirpath != self.path:
                os.rmdir(dirpath)

        # delete unreferenced files
        for dirpath, _, filenames in os.walk(self.path):
            for filename in filenames:
                abs_path = os.path.join(dirpath, filename)
                rel_path = abs_path[len(self.path) + 1:]
                if rel_path not in self.filepath_file_map:
                    os.remove(abs_path)

        self.last_action = LocalDirectoryRepositoryState.PRUNE

    def _contains(self, path_to_test: str) -> bool:
        '''
        Returns whether the given file is part of the directory tree.
        '''
        return os.path.abspath(path_to_test).startswith(self.path + os.sep)
