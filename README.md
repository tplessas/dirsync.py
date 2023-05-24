# dirsync.py

A Python tool to maintain an up-to-date replica of a repository (any
location where files are stored, currently limited to `local directory 
-> local directory` use cases only). Tested on Linux, should work on
Windows.

This tool started as a take-home assignment for a job - I admittedly 
might have gotten a bit carried away while implementing it though,
giving myself a new pet project in the process.

## Usage

Download the `dirsync` directory and execute the project from one level
above in the filesystem. Exit using `CTRL + C`.

    $ python -m dirsync -h

    usage: python -m dirsync [-h] src_dir dest_dir logfile_path interval_ms

    A Python tool to maintain an up-to-date replica of a repository.

    positional arguments:
        src_dir       source repository to be synced
        dest_dir      destination/replica repository
        logfile_path  path where the sync logfile will be written
        interval_ms   frequency of execution of sync task in milliseconds

    options:
        -h, --help    show this help message and exit

For `local directory -> local directory` sync the directories have to be
created in advance, and the destination directory has to be empty.

## Architecture/Approach

The application essentially periodically monitors the source repository for
changes in files, logs them, and "replays" them in the destination directory
to achieve replication.

The sync mechanism is fully decoupled from the repository implementation
using interfaces and dependency injection. New repositories (e.g. remote
filesystems, object buckets etc.) can thus be straightforwardly added by 
implementing the Repository and File APIs in concrete classes.

The Repository API exposes functions related to the basic operations that
may take place in a file store (create/modify/move/copy/delete), as well as
repository monitoring and file reference retrieval ones. The File API deals
with hash calculation and file reading.

## Limitations

- **File metadata are not synced** due to the "replay" sync mechanism.
- **Empty directories are not tracked**, and are only synced when at least
one file is added to them - somewhat like how `git` works.

## Todo

- **Add tests** - a bit ironic those are missing since this was meant for a
QA role, eh? I had to submit the project at some point, though, so corners
were cut in this department.  
Unit tests have to be added for the CLI and repository/file classes of course,
as well as some integration tests to automate the testing of sync operations
from program launch to interruption.
- **Simplify Repository API** - since the hashes of the files are always
available the only operations the Repository API needs to expose are
create/modify/delete (again, just like how `git` works), which are sufficient
for an equally efficient implementation of the sync mechanism (given move/copy
are special cases/combinations of create/delete operations).  
I unfortunately only realized this a bit too late in the implementation
process.