from pytlas.skill import handlers, module_metas, Meta
from pytlas.localization import get_translations
from pytlas.utils import get_package_name_from_module, rmtree
import re, logging, os, subprocess, pytlas.settings as settings

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

def install_dependencies_if_needed(directory, stdout=None):
  """Install skill dependencies if a requirements.txt file is present.

  Args:
    directory (str): Skill directory
    stdout (func): Function to call to output something

  """

  if os.path.isfile(os.path.join(directory, 'requirements.txt')):
    if stdout: # pragma: no cover
      stdout('  Installing dependencies')

    logging.info('Installing skill dependencies from "%s"' % directory)

    subprocess.check_output(['pip', 'install', '-r', 'requirements.txt'],
      stderr=subprocess.STDOUT,
      cwd=directory)
  elif stdout: # pragma: no cover
    stdout('  No requirements.txt available, skipping')

def install_skills(directory, stdout=None, *names):
  """Install or update given skills.

  Args:
    directory (str): Skills directory
    stdout (func): Function to call to output something
    names (list of str): list of skills to install

  Returns:
    list of str: List of installed or updated skills

  """

  installed_skills = []

  for name in names:
    url = name
    owner, repo = skill_parts_from_name(name)

    if stdout: # pragma: no cover
      stdout('Processing %s/%s' % (owner, repo))

    dest = os.path.abspath(os.path.join(directory, to_skill_folder(owner, repo)))

    if name.startswith(owner):
      url =  settings.get(settings.SETTING_DEFAULT_REPO_URL) + name

    logging.info('Will download skill from "%s" to "%s"' % (url, dest))

    if os.path.isdir(dest):
      if stdout: # pragma: no cover
        stdout('  Skill folder already exists, updating')
            
      installed_skills.extend(update_skills(directory, stdout, name))

      continue

    try:
      if stdout: # pragma: no cover
        stdout('  Cloning skill repository')

      subprocess.check_output(['git', 'clone', url, dest], stderr=subprocess.STDOUT)

      logging.info('Successfully cloned skill "%s"' % repo)

      install_dependencies_if_needed(dest, stdout)

      if stdout: # pragma: no cover
        stdout('  ✔️ Installed')

      logging.info('Successfully installed "%s"' % repo)

      installed_skills.append(name)
    except subprocess.CalledProcessError as e:
      if stdout: # pragma: no cover
        stdout('  ❌ Failed')
        
      logging.error("Could not clone the skill repo, make sure you didn't mispelled it and you have sufficient rights to clone it. \"%s\"" % e)
    
  return installed_skills

def update_skills(directory, stdout=None, *names):
  """Update given skills.

  Args:
    directory (str): Skills directory
    stdout (func): Function to call to output something
    names (list of str): list of skills to update

  Returns:
    list of str: List of updated skills

  """

  updated_skills = []
  names = names or os.listdir(directory)

  for name in names:
    if stdout: # pragma: no cover
      stdout('Processing %s' % name)

    try:
      owner, repo = skill_parts_from_name(name)
      folder_name = to_skill_folder(owner, repo)
    except:
      folder_name = name
      
    folder = os.path.abspath(os.path.join(directory, folder_name))

    if not os.path.isdir(os.path.join(folder, '.git')):
      if stdout: # pragma: no cover
        stdout('  Not a git repository, could not update it')
      
      logging.warning('"%s" is not a git repository, skipping update' % folder)

      continue

    try:
      subprocess.check_output(['git', 'pull'], cwd=folder, stderr=subprocess.STDOUT)

      install_dependencies_if_needed(folder, stdout)

      if stdout: # pragma: no cover
        stdout('  ✔️ Updated')
      
      logging.info('Updated "%s"' % name)

      updated_skills.append(from_skill_folder(folder_name))
      
    except subprocess.CalledProcessError as e:
      if stdout: # pragma: no cover
        stdout('  ❌ Failed')

      logging.error('Could not pull in "%s": "%s"' % (folder, e))
  
  return updated_skills

def uninstall_skills(directory, stdout=None, *names):
  """Uninstall given skills.

  Args:
    directory (str): Skills directory
    stdout (func): Function to call to output something
    names (list of str): list of skills to uninstall

  Returns:
    list of str: List of removed skills

  """

  removed_skills = []

  for name in names:
    if stdout: # pragma: no cover
      stdout('Processing %s' % name)
    
    owner, repo = skill_parts_from_name(name)
    folder = os.path.abspath(os.path.join(directory, to_skill_folder(owner, repo)))

    if not os.path.isdir(folder):
      logging.error('Skill "%s" does not seems to be installed in "%s"' % (name, folder))
      continue

    logging.info('Removing "%s"' % folder)

    try:
      rmtree(folder)

      if stdout: # pragma: no cover
        stdout('  ✔️ Uninstalled')
      
      removed_skills.append(name)
    except Exception as e:
      if stdout: # pragma: no cover
        stdout('  ❌ Failed')

      logging.error('Could not delete the "%s" skill folder: "%s"' % (folder, e))

  return removed_skills

def get_loaded_skills(lang):
  """Retrieve installed and loaded skills. You must call import_skills first if 
  you want them to show in the results.

  Args:
    lang (str): Language code to translate skills name and description

  Returns:
    list of Meta: Skills loaded.

  """

  unique_pkgs = list(set(get_package_name_from_module(v.__module__) for v in handlers.values()))
  skills_meta = []

  for pkg in unique_pkgs:
    meta = {}
    meta_func = module_metas.get(pkg)

    if meta_func:
      translations = get_translations(lang).get(pkg, {})
      meta = meta_func(lambda k: translations.get(k, k))

      if not isinstance(meta, Meta):
        meta = Meta(**meta)
    else:
      meta = Meta(from_skill_folder(pkg))

    skills_meta.append(meta)

  return skills_meta
