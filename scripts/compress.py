#! /usr/bin/env python
import os
import tarfile


def tar_bzip2_directory(directory, outfile, ignore_extensions=None):
    '''
    Takes a directory and creates a tar.bz2 file
    ignore_extensions can be a list of 4-char strings: ['.fvs','.trl']
    '''
    if not ignore_extensions:
        ignore_extensions = []

    with tarfile.open(outfile, 'w:bz2') as tar:
        for dirpath, dirnames, filenames in os.walk(directory):
            for file in filenames:
                if file[-4:] not in ignore_extensions:
                    tar.add(os.path.join(dirpath, file))
    return outfile
