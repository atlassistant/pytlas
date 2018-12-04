from pytlas.skill import handlers, module_metas
from pytlas.localization import module_translations
from pytlas.utils import get_package_name_from_module

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
""".format(**self.__dict__)

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
