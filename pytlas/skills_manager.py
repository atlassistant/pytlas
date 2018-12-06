from pytlas.skill import handlers, module_metas
from pytlas.localization import module_translations
from pytlas.utils import get_package_name_from_module
import re, logging, os, subprocess

DEFAULT_REPO_URL = os.environ.get('PYTLAS_DEFAULT_REPO_URL', 'https://github.com/')

class SkillData:
  """Represents a single skill data.
  """

  def __init__(self, package, name=None, description='No description provided',
    version='?.?.?', author='', homepage=''):
    self.package = package
    self.name = name or package
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

def skill_parts_from_url(path):
  """Retrieve the skill namespace and repository.

  Args:
    path (str): Relative or absolute path of a git repository

  Examples:
    >>> skill_parts_from_url('atlassistant/weather')
    ('atlassistant', 'weather')

    >>> skill_parts_from_url('https://github.com/atlassistant/weather')
    ('atlassistant', 'weather')

    >>> skill_parts_from_url('git@github.com:atlassistant/weather.git')
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

def install_skills(directory, *names):
  """Install or update given skills.

  Args:
    directory (str): Skills directory
    names (list of str): list of skills to install

  Returns:
    list of str: List of successfuly installed skills

  """

  installed_skills = []

  for name in names:
    url = name
    owner, repo = skill_parts_from_url(name)
    dest = os.path.join(directory, '%s_%s' % (owner, repo))

    if name.startswith(owner):
      url = DEFAULT_REPO_URL + name

    logging.info('Will download skill from "%s" to "%s"' % (url, dest))

    if os.path.isdir(dest):
      logging.warning('Skill already exists, will update it')
      installed_skills.append(repo)
      continue

    try:
      output = subprocess.check_output(['git', 'clone', url, dest], shell=True, stderr=subprocess.STDOUT)

      logging.info('Successfully downloaded skill "%s", will process dependencies' % repo)

      installed_skills.append(repo)
    except subprocess.CalledProcessError as e:
      logging.error("Could not clone the skill repo, make sure you didn't mispelled it and you have sufficient rights to clone it. \"%s\"" % e)

  return installed_skills

def uninstall_skills(directory, *names):
  """Uninstall given skills.

  Args:
    directory (str): Skills directory
    names (list of str): list of skills to install

  """

  pass

def get_installed_skills(lang):
  """Retrieve installed and loaded skills.

  Args:
    lang (str): Language code to translate skills name and description

  Returns:
    list of SkillData: Skills retrieved.

  """

  unique_pkgs = list(set(get_package_name_from_module(v.__module__) for v in handlers.values()))
  skills = []

  for pkg in unique_pkgs:
    meta = {}
    meta_func = module_metas.get(pkg)

    if meta_func:
      translations = module_translations.get(pkg, {}).get(lang, {})
      meta = meta_func(lambda k: translations.get(k, k))

    skills.append(SkillData(pkg, **meta))

  return skills
