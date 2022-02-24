
from codecs import open
from os import path
from setuptools import setup, find_packages


__version__ = '1.0.299'


here = path.abspath(path.dirname(__file__))


if path.isfile(path.join(here, 'README.md')):
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = ""

setup(
    name='benchmark-runner',
    version=__version__,
    description='Benchmark Runner Tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Red Hat',
    author_email='ebattat@redhat.com',
    url='',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    zip_safe=False,

    # Find all packages (__init__.py)
    packages=find_packages(include=['benchmark_runner', 'benchmark_runner.*']),

    install_requires=[
        'typing==3.7.4.3',
        'elasticsearch==7.16.1',
        'elasticsearch_dsl==7.4.0',  # for deep search
        'pandas',  # required latest
        'jinja2==3.0.3',
        'typeguard==2.12.1',
        'PyYAML==6.0',
        'azure==4.0.0',
        'paramiko==2.8.0',
        'tenacity==8.0.1',  # retry decorator
        'PyGitHub==1.55',  # update secrets
        'myst-parser==0.16.0',  # readthedocs
        'boto3==1.20.24',  # s3
        'botocore==1.23.24',  # s3
        "sphinx==4.0.2",  # readthedocs
        "sphinx_rtd_theme==0.4.3",  # readthedocs
        # must add new package inside requirements.txt
    ],

    setup_requires=['pytest', 'pytest-runner', 'wheel', 'coverage'],

    include_package_data=True,

    # dependency_links=[]
)
