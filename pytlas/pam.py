from pytlas.skill import handlers, module_metas
from pytlas.localization import module_translations
from pytlas.utils import get_package_name_from_module
from shutil import rmtree
import re, logging, os, subprocess

DEFAULT_REPO_URL = os.environ.get('PYTLAS_DEFAULT_REPO_URL', 'https://github.com/')
SKILL_FOLDER_SEPARATOR = '__'

def skill_parts_from_name(path):
  """Retrieve the skill namespace and repository.

  Args:
    path (str): Relative or absolute path of a git repository

  Examples:
    >>> skill_parts_from_name('atlassistant/weather')
    ('atlassistant', 'weather')

    >>> skill_parts_from_name('https://github.com/atlassistant/weather')
    ('atlassistant', 'weather')

    >>> skill_parts_from_name('git@github.com:atlassistant/weather.git')
    ('atlassistant', 'weather')

  """

  # Here we need to handle absolute url such as git@<a host> or https://<an url>
  matches = [(m.start(), m.end()) for m in re.finditer(':|/', path)]

  if len (matches) == 0:
    raise Exception('Could not determine owner and repo names')

  last_slash_idx = matches[-1][0]

  if len (matches) > 1:
    pre_idx = matches[-2][0] + 1
    path = path[pre_idx:]
    last_slash_idx -= pre_idx

  owner = path[:last_slash_idx]
  repo = path[last_slash_idx + 1:]

  # handle .git extension on repo
  try:
    ext_idx = repo.index('.')
    repo = repo[:ext_idx]
  except:
    pass
  
  return (owner, repo)

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
    return "%s/%s" % (parts[0], parts[1])

  return parts[0]


class SkillData:
  """Represents a single skill data.
  """

  def __init__(self, package, name=None, description='No description provided',
    version='?.?.?', author='', homepage='', media=''):
    self.package = package
    self.name = name or package
    self.media = media
    self.description = description
    self.version = version
    self.author = author
    self.homepage = homepage

  def __str__(self):
    return """{name} - v{version}
  description: {description}
  homepage: {homepage}
  author: {author}
  package: {package}
""".format(**self.__dict__)

def install_dependencies_if_needed(directory, stdout=None):
  """Install skill dependencies if a requirements.txt file is present.

  Args:
    directory (str): Skill directory
    stdout (func): Function to call to output something

  """

  if os.path.isfile(os.path.join(directory, 'requirements.txt')):
    if stdout:
      stdout('  Installing dependencies')

    logging.info('Installing skill dependencies from "%s"' % directory)

    subprocess.check_output(['pip', 'install', '-r', 'requirements.txt'], 
      shell=True, 
      stderr=subprocess.STDOUT,
      cwd=directory)
  elif stdout:
    stdout('  No requirements.txt available, skipping')

def install_skills(directory, stdout=None, *names):
  """Install or update given skills.

  Args:
    directory (str): Skills directory
    stdout (func): Function to call to output something
    names (list of str): list of skills to install

  """

  for name in names:
    url = name
    owner, repo = skill_parts_from_name(name)

    if stdout:
      stdout('Processing %s/%s' % (owner, repo))

    dest = os.path.abspath(os.path.join(directory, to_skill_folder(owner, repo)))

    if name.startswith(owner):
      url = DEFAULT_REPO_URL + name

    logging.info('Will download skill from "%s" to "%s"' % (url, dest))

    if os.path.isdir(dest):
      if stdout:
        stdout('  Skill folder already exists, updating')

      logging.warning('Skill already exists, will update it')

      continue

    try:
      if stdout:
        stdout('  Cloning skill repository')

      subprocess.check_output(['git', 'clone', url, dest], shell=True, stderr=subprocess.STDOUT)

      logging.info('Successfully cloned skill "%s"' % repo)

      install_dependencies_if_needed(dest, stdout)      

      if stdout:
        stdout('  Installed! ✔️')

      logging.info('Successfully installed "%s"' % repo)
    except subprocess.CalledProcessError as e:
      if stdout:
        stdout('  Failed ❌')
        
      logging.error("Could not clone the skill repo, make sure you didn't mispelled it and you have sufficient rights to clone it. \"%s\"" % e)

def update_skills(directory, stdout, *names):
  """Update given skills.

  Args:
    directory (str): Skills directory
    stdout (func): Function to call to output something
    names (list of str): list of skills to update

  """

  names = names or os.listdir(directory)

  for name in names:
    if stdout:
      stdout('Processing %s' % name)

    try:
      owner, repo = skill_parts_from_name(name)
      folder_name = to_skill_folder(owner, repo)
    except:
      folder_name = name
      
    folder = os.path.abspath(os.path.join(directory, folder_name))

    if not os.path.isdir(os.path.join(folder, '.git')):
      if stdout:
        stdout('  Not a git repository, could not update it')
      
      logging.warning('"%s" is not a git repository, skipping update' % folder)

      continue

    try:
      subprocess.check_output(['git', 'pull'], shell=True, cwd=folder, stderr=subprocess.STDOUT)

      if stdout:
        stdout('  Updated ✔️')
      
      logging.info('Updated "%s"' % name)
    except subprocess.CalledProcessError as e:
      if stdout:
        stdout('  Failed to update ❌')

      logging.error('Could not pull in "%s": "%s"' % (folder, e))

def uninstall_skills(directory, stdout, *names):
  """Uninstall given skills.

  Args:
    directory (str): Skills directory
    stdout (func): Function to call to output something
    names (list of str): list of skills to uninstall

  """

  for name in names:
    if stdout:
      stdout('Processing %s' % name)
    
    owner, repo = skill_parts_from_name(name)
    folder = os.path.abspath(os.path.join(directory, to_skill_folder(owner, repo)))

    if not os.path.isdir(folder):
      logging.error('Skill "%s" does not seems to be installed in "%s"' % (name, folder))
      continue

    logging.info('Removing "%s"' % folder)

    try:
      rmtree(folder)

      if stdout:
        stdout('  Uninstalled ✔️')
      
      logging.info('Uninstalled "%s"' % repo)
    except Exception as e:
      if stdout:
        stdout('  Failed ❌')

      logging.error('Could not delete the "%s" skill folder: "%s"' % (folder, e))

def get_installed_skills(lang):
  """Retrieve installed and loaded skills. You must call import_skills first if 
  you want them to show in the results.

  Args:
    lang (str): Language code to translate skills name and description

  Returns:
    list of SkillData: Skills retrieved.

  """

  unique_pkgs = list(set(from_skill_folder(get_package_name_from_module(v.__module__)) for v in handlers.values()))
  skills = []

  for pkg in unique_pkgs:
    meta = {}
    meta_func = module_metas.get(pkg)

    if meta_func:
      translations = module_translations.get(pkg, {}).get(lang, {})
      meta = meta_func(lambda k: translations.get(k, k))

    skills.append(SkillData(pkg, **meta))

  return skills
