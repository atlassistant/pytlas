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
  install_requires=[
    'transitions==0.6.4',
    'fuzzywuzzy==0.16.0',
    'colorlog==2.2.0',
    'pychatl==1.2.2',
    'python-dateutil==2.7.3',
    'Babel==2.6.0',
    'requests==2.19.1', # requests is included because the remote training will need it
  ],
  extras_require={
    'snips': [
      'snips-nlu==0.17.3',
    ],
    'test': [
      'nose==1.3.7',
      'sure==1.4.11',
      'coverage==4.5.1',
    ],
    'watch': [
      'watchgod==0.2',
    ],
  },
  entry_points={
    'console_scripts': [
      'pytlas = pytlas.cli:main',
    ]
  },
)