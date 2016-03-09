# -*- coding: utf-8 -*-
"""
    idtools.utils
    ~~~~~~~~~~~~~

    General utilities.

    :copyright: (c) 2016 Wibowo Arindrarto <bow@bow.web.id>
    :license: BSD

"""
import sys
from contextlib import contextmanager

import click


if sys.version_info[0] > 2:
    basestring = str


@contextmanager
def get_handle(input, encoding=None, mode="r"):
    """Context manager for opening files.

    This function returns a file handle of the given file name. You may also
    give an open file handle, in which case the file handle will be yielded
    immediately. The purpose of this is to allow the context manager handle
    both file objects and file names as inputs.

    If a file handle is given, it is not closed upon exiting the context.
    If a file name is given, it will be closed upon exit.

    :param input: Handle of open file or file name.
    :type input: file handle or obj
    :param encoding: Encoding of the file. Ignored if input is file handle.
    :type encoding: str
    :param mode: Mode for opening file. Ignored if input is file handle.
    :type mode: str

    """
    if isinstance(input, basestring):
        assert isinstance(input, basestring), \
            "Unexpected input type: " + repr(input)
        fh = click.open_file(input, mode=mode, encoding=encoding)
    else:
        fh = input

    yield fh

    if isinstance(input, basestring):
        fh.close()
