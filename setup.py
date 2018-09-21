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
    'watchgod==0.2',
    'pychatl==1.2.0',
    'python-dateutil==2.7.3',
  ],
  extras_require={
    'snips': [
      'snips-nlu==0.16.5',
    ],
  },
  entry_points={
    'console_scripts': [
      'pytlas = pytlas.cli:main',
    ]
  },
)