"""ioutils provides helper methods to deal with file stuff.
"""

import os
import stat
from typing import Callable
from shutil import rmtree as shrmtree


def read_file(path: str, ignore_errors=False, relative_to: str = None) -> str:
    """Read the file content as utf-8 at the specified path.

    Args:
      path (str): Path to be read
      ignore_errors: True if you don't want exception to be raised (None will be returned)
      relative_to (str): If set, the path will be evaluated relative to this file or folder

    Returns:
      str: Content of the file or None if not found and ignore_errors was true

    """
    if relative_to:
        dirname = relative_to if os.path.isdir(relative_to) else os.path.dirname(relative_to)
        path = os.path.join(dirname, path)

    try:
        with open(path, encoding='utf-8') as file:
            return file.read()
    except Exception as err: # pylint: disable=broad-except
        if not ignore_errors:
            raise err

        return None


def _onerror(func: Callable, path: str, exc_info) -> None:  # pragma: no cover
    """Error handler for ``shutil.rmtree``.

    If the error is due to an access error (read only file)
    it attempts to add write permission and then retries.

    If the error is for another reason it re-raises the error.

    """
    if not os.access(path, os.W_OK):
            # Is the error an access error ?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise # pylint: disable=misplaced-bare-raise


def rmtree(path: str, ignore_errors=False) -> None:
    """Recursively deletes a folder and its children and handle readonly files as per
    https://stackoverflow.com/a/2656405/7641999.

    Args:
      path (str): Path to delete
      ignore_errors (bool): Should we ignore errors

    """
    shrmtree(path, ignore_errors=ignore_errors, onerror=_onerror)
