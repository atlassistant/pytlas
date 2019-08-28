# pylint: disable=C0111

from setuptools import setup, find_packages

with open('README.rst', encoding='utf-8') as f:
    README = f.read()

with open('pytlas/version.py') as f:
    VERSION = f.readlines()[1].strip()[15:-1]

setup(
    name='pytlas',
    version=VERSION,
    description='An open-source Python 3 assistant library built for people and '\
                'made to be super easy to setup and understand!',
    long_description=README,
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
        'transitions~=0.7.0',
        'fuzzywuzzy~=0.17.0',
        'colorlog~=4.0.2',
        'pychatl~=2.0.1',
        'python-dateutil~=2.8.0',
        'Babel~=2.7.0',
        # Those lines are required for markdown display and raw_text generation
        'Markdown~=3.1.1',
        'beautifulsoup4~=4.8.0',
    ],
    extras_require={
        'snips': [
            # For snips, target a specific version since it may break sometimes
            'snips-nlu==0.20.0',
        ],
        'test': [
            'nose~=1.3.7',
            'sure~=1.4.11',
            'coverage~=4.5.4',
        ],
        'watch': [
            'watchgod~=0.4',
        ],
        'docs': [
            'sphinx~=1.7.5',
            'sphinx_rtd_theme~=0.4.3',
        ],
    },
    entry_points={
        'console_scripts': [
            'pytlas = pytlas.cli:main',
        ]
    },
)
