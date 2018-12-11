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