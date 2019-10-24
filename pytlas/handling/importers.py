# pylint: disable=missing-module-docstring

import importlib
import os
import logging
import sys
import threading
from types import ModuleType


def _reload(module: ModuleType) -> None:
    """Recursively reloads a module. It only works for simple scenario but it may
    be suitable for pytlas ;)

    Args:
      module (ModuleType): Module to reload

    """
    importlib.reload(module)

    for attr_name in dir(module):
        attr = getattr(module, attr_name)

        if isinstance(attr, ModuleType):
            _reload(attr)


def import_or_reload(module_name: str) -> None:
    """Import or reload the given module name.

    Args:
      module_name (str): Module name

    """
    module = sys.modules.get(module_name)

    if module:
        logging.info('Reloading module "%s"', module_name)

        try:
            _reload(module)
        except Exception as err: # pylint: disable=W0703
            logging.warning('Reloading failed for "%s": %s', module_name, err)
    else:
        logging.info('Importing module "%s"', module_name)

        try:
            importlib.import_module(module_name)
        except ImportError:
            logging.error('Could not import module "%s"', module_name)


def _watch(directory: str) -> None: # pragma: no cover
    try:
        from watchgod import watch # pylint: disable=import-outside-toplevel
    except ImportError:
        logging.error(
            'Could not watch for file changes, is "watchgod" installed?')
        return

    logging.info('Watching for file changes in "%s"', directory)

    for changes in watch(directory):
        for change in changes:
            file_path = change[1]
            module_name = os.path.split(
                os.path.relpath(file_path, directory))[0]

            logging.debug('Changes in file "%s" cause "%s" module (re)load',
                          file_path, module_name)

            import_or_reload(module_name)


def import_skills(directory: str, auto_reload=False) -> None:
    """Import skills inside the givne directory.

    Args:
      directory (str): Directory in which skills are contained
      auto_reload (bool): Sets to True if you want to watch for file changes, it
        should be used only for development purposes

    """
    logging.info('Importing skills from "%s"', directory)

    if not os.path.isdir(directory):
        logging.info('Directory "%s" does not exist, no skills will be loaded 🤔', directory)
    else:
        sys.path.append(directory)

        for skill_folder in os.listdir(directory):
            import_or_reload(skill_folder)

        if auto_reload: # pragma: no cover
            threading.Thread(target=_watch, args=(directory,), daemon=True).start()
