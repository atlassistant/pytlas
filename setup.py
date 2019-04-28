from setuptools import setup, find_packages
import os

with open('README.rst', encoding='utf-8') as f:
  readme = f.read()

with open('pytlas/version.py') as f:
  version = f.readline().strip()[15:-1]

setup(
  name='pytlas',
  version=version,
  description='Python 3 assistant made to be super simple to setup!',
  long_description=readme,
  url='https://github.com/atlassistant/pytlas',
  author='Julien LEICHER',
  license='GPL-3.0',
  packages=find_packages(),
  include_package_data=True,
  classifiers=[
    "Programming Language :: Python :: 3",
  ],
  install_requires=[
    'click~=7.0',
    'transitions~=0.6.9',
    'fuzzywuzzy~=0.16.0',
    'colorlog~=3.1.4',
    'pychatl~=1.2.7',
    'python-dateutil~=2.7.3',
    'Babel~=2.6.0',
    # requests is included because the remote training will need it
    'requests~=2.20.0',
    # Those lines are required for markdown display and raw_text generation
    'Markdown~=3.0.1',
    'beautifulsoup4~=4.6.3',
  ],
  extras_require={
    'snips': [
      # For snips, target a specific version since it may break sometimes
      'snips-nlu==0.19.6',
    ],
    'test': [
      'nose~=1.3.7',
      'sure~=1.4.11',
      'coverage~=4.5.1',
    ],
    'watch': [
      'watchgod~=0.2',
    ],
    'docs': [
      'sphinx~=1.7.5',
      'sphinx_rtd_theme~=0.4.2',
    ],
  },
  entry_points={
    'console_scripts': [
      'pytlas = pytlas.cli:main',
    ]
  },
)