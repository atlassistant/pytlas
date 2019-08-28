# pylint: disable=C0111

import logging
import re
import os
import subprocess
from pytlas.handling.skill import GLOBAL_METAS, GLOBAL_HANDLERS, Meta
from pytlas.pkgutils import get_package_name_from_module
from pytlas.ioutils import rmtree


def extract_repo_data(path):
    """Retrieve the skill owner and repository.

    Args:
      path (str): Relative or absolute path of a git repository

    Returns:
      (str, str): Respectively, owner and repository extracted

    Examples:
      >>> extract_repo_data('atlassistant/weather')
      ('atlassistant', 'weather')

      >>> extract_repo_data('https://github.com/atlassistant/weather')
      ('atlassistant', 'weather')

      >>> extract_repo_data('git@github.com:atlassistant/weather.git')
      ('atlassistant', 'weather')

    """
    # Here we need to handle absolute url such as git@<a host> or https://<an url>
    matches = [(m.start(), m.end()) for m in re.finditer(':|/', path)]

    if not matches:
        raise Exception('Could not determine owner and repo names')

    last_slash_idx = matches[-1][0]

    if len(matches) > 1:
        pre_idx = matches[-2][0] + 1
        path = path[pre_idx:]
        last_slash_idx -= pre_idx

    owner = path[:last_slash_idx]
    repo = path[last_slash_idx + 1:]

    # handle .git extension on repo
    try:
        ext_idx = repo.index('.')
        repo = repo[:ext_idx]
    except:  # pylint: disable=W0702
        pass

    return (owner, repo)


DISPLAY_NAME_SEPARATOR = '/'


def to_display_name(owner, repo):
    """Returns the display name for the given owner and repo.

    Args:
      owner (str): Owner of the repository
      repo (str): Repository

    Returns:
      str: Display name

    Examples:
      >>> to_display_name('atlassistant', 'weather')
      'atlassistant/weather'

    """
    return owner + DISPLAY_NAME_SEPARATOR + repo


SKILL_FOLDER_SEPARATOR = '__'


def to_skill_folder(owner, repo):
    """Gets the skill folder name from owner and repo.

    Args:
      owner (str): Owner of the repository
      repo (str): Repository name

    Returns:
      str: Skill folder name

    Examples:
      >>> to_skill_folder('atlassistant', 'weather')
      'atlassistant__weather'

    """
    return owner + SKILL_FOLDER_SEPARATOR + repo


def from_skill_folder(folder):
    """Gets the skill package name in the form owner/repo from the given folder.

    Args:
      folder (str): Folder name

    Returns:
      str: Skill package name

    Examples:
      >>> from_skill_folder('weather')
      'weather'

      >>> from_skill_folder('atlassistant__weather')
      'atlassistant/weather'

    """
    parts = folder.split(SKILL_FOLDER_SEPARATOR)

    if len(parts) > 1:
        return to_display_name(parts[0], parts[1])

    return parts[0]


def path_to_skill_folder(path):
    """Convert a skill name to a folder representation for pytlas.

    Args:
      path (str): Path of a skill in absolute or relative url

    Returns:
      str: Folder name in the skill folder

    Examples:
      >>> path_to_skill_folder('atlassistant/weather')
      'atlassistant__weather'
      >>> path_to_skill_folder('https://gitlab.com/atlassistant/weather')
      'atlassistant__weather'
      >>> path_to_skill_folder('weather')
      'weather'
      >>> path_to_skill_folder('atlassistant__weather')
      'atlassistant__weather'

    """
    try:
        owner, repo = extract_repo_data(path)
        return to_skill_folder(owner, repo)
    except:  # pylint: disable=W0702
        return path


class SkillsManager:
    """The SkillsManager handles skill installation, updates, listing and removal.
    It can be used with the built-in CLI or used as a library.
    """

    # pylint: disable=R0913

    def __init__(self, directory, lang='en', default_git_url='https://github.com/',
                 handlers_store=None, metas_store=None):
        """Instantiate a new SkillManager for the given directory.

        Args:
          directory (str): Skill directory
          lang (str): Language used to translate skill metadata
          default_git_url (str): Default git base url used for relative skill names
          handlers_store (HandlersStore): Handlers store used to enumerate loaded skills
          metas_store (MetasStore): Metas store used when listing skills data

        """
        self._logger = logging.getLogger('skm')
        self._directory = directory
        self.lang = lang
        self._default_git_url = default_git_url
        self._metas = metas_store or GLOBAL_METAS
        self._handlers = handlers_store or GLOBAL_HANDLERS

    # pylint: enable=R0913

    def get(self):
        """Retrieve currently loaded skills. That means you should first start to
        imports them by using the `pytlas.handling.importers` namespace.

        Returns:
          list of Meta: Skills loaded.

        """
        unique_pkgs = list(set(get_package_name_from_module(
            v.__module__) for v in self._handlers._data.values()))  # pylint: disable=W0212
        self._logger.info(
            'Retrieving meta for "%d" unique packages', len(unique_pkgs))
        skills_meta = []

        for pkg in unique_pkgs:
            meta = self._metas.get(pkg, self.lang) or Meta(
                from_skill_folder(pkg))
            skills_meta.append(meta)

        return skills_meta

    def install(self, *names):
        """Install or update given skill names.

        Args:
          names (list of str): Skills to install/update

        Returns:
          (list of str, list of str): Respectively, successful installs and failed ones

        """
        succeeded = []
        failed = []

        for name in names:
            url = name
            owner, repo = extract_repo_data(name)
            display_name = to_display_name(owner, repo)

            if name.startswith(owner):  # Relative name, prepend the default git url
                url = self._default_git_url + name

            self._logger.info('Processing "%s" from "%s"', display_name, url)
            dest = os.path.abspath(os.path.join(
                self._directory, to_skill_folder(owner, repo)))

            if os.path.isdir(dest):
                self._logger.info(
                    'Skill "%s" already exists, let\'s try an update', repo)
                succ, fail = self.update(name)
                succeeded.extend(succ)
                failed.extend(fail)
            else:
                try:
                    self._logger.info(
                        'Starting to clone "%s" inside "%s"', url, dest)
                    subprocess.check_output(
                        ['git', 'clone', url, dest], stderr=subprocess.STDOUT)

                    self._install_dependencies(dest)

                    succeeded.append(display_name)
                    logging.info('Successfully installed "%s"', repo)
                except subprocess.CalledProcessError as err:
                    failed.append(display_name)
                    self._logger.error(
                        'Could not clone the skill repo, make sure you didn\'t mispelled it and '
                        'you have sufficient rights to clone it. "%s"', err)
                    rmtree(dest, ignore_errors=True) # try to clean up the directory

        return (succeeded, failed)

    def update(self, *names):
        """Update given skill names.

        Args:
          names (list of str): Skills to update, if no one is given, all skills will be updated

        Returns:
          (list of str, list of str): Respectively, successful updates and failed ones

        """
        to_proceed = names or os.listdir(self._directory)
        succeeded = []
        failed = []

        for name in to_proceed:
            folder_name = path_to_skill_folder(name)
            display_name = from_skill_folder(folder_name)
            self._logger.info('Updating "%s"', display_name)
            folder = os.path.abspath(
                os.path.join(self._directory, folder_name))

            if not os.path.isdir(os.path.join(folder, '.git')):
                failed.append(display_name)
                self._logger.warning(
                    'Not a git repository "%s", skipping', folder)
            else:
                try:
                    self._logger.info('Pulling updates for "%s"', display_name)
                    subprocess.check_output(
                        ['git', 'pull'], cwd=folder, stderr=subprocess.STDOUT)

                    self._install_dependencies(folder)

                    succeeded.append(display_name)
                    self._logger.info(
                        'Successfully updated "%s"', display_name)
                except subprocess.CalledProcessError as err:
                    failed.append(display_name)
                    self._logger.error(
                        'Could not pull in "%s": "%s"', folder, err)

        return (succeeded, failed)

    def uninstall(self, *names):
        """Uninstall given skill names.

        Args:
          names (list of str): Skills to remove

        Returns:
          (list of str, list of str): Respectively, successful removes and failed ones

        """
        succeeded = []
        failed = []

        for name in names:
            folder_name = path_to_skill_folder(name)
            display_name = from_skill_folder(folder_name)
            folder = os.path.abspath(
                os.path.join(self._directory, folder_name))

            if not os.path.isdir(folder):
                failed.append(display_name)
                self._logger.warning(
                    'Skill "%s" does not seems to be installed in "%s", skipping',
                    display_name, folder)
            else:
                self._logger.info('Removing "%s"', folder)
                try:
                    rmtree(folder)
                    succeeded.append(display_name)
                    self._logger.info(
                        'Successfully uninstalled "%s"', display_name)
                except Exception as err:  # pylint: disable=W0703
                    failed.append(display_name)
                    self._logger.error(
                        'Could not delete "%s": "%s"', folder, err)

        return (succeeded, failed)

    def _install_dependencies(self, directory):
        requirements_path = os.path.join(directory, 'requirements.txt')

        if os.path.isfile(requirements_path):
            self._logger.info(
                'Installing dependencies from "%s"', requirements_path)
            subprocess.check_output(['pip', 'install', '-r', 'requirements.txt'],
                                    stderr=subprocess.STDOUT, cwd=directory)
        else:
            self._logger.info(
                'No requirements.txt available inside "%s", skipping', directory)
