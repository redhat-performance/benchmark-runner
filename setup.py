
from codecs import open
from os import path
from setuptools import setup, find_packages


__version__ = '1.0.699'  # update also .bumpversion.cfg


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
    url='https://github.com/redhat-performance/benchmark-runner',
    license="Apache License 2.0",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],

    zip_safe=False,

    # Find all packages (__init__.py)
    packages=find_packages(include=['benchmark_runner', 'benchmark_runner.*']),

    install_requires=[
        'attrs==21.4.0',  # readthedocs
        'azure==4.0.0',
        'boto3==1.33.13',  # s3
        'botocore==1.33.13',  # s3
        'cryptography==43.0.1',  # for paramiko
        'elasticsearch==7.16.1',
        'elasticsearch-dsl==7.4.0',  # for deep search
        'google-auth==2.30.0',  # for Google Drive
        'google-auth-httplib2==0.2.0',  # for Google Drive
        'google-auth-oauthlib==1.2.0',  # for Google Drive
        'google-api-python-client==2.135.0',  # for Google Drive
        'ipywidgets==8.0.6',  # for jupyterlab widgets
        'jinja2==3.1.4',  # for yaml templates and df.style
        'myst-parser==1.0.0',  # readthedocs
        'openshift-client==1.0.17',  # clusterbuster && prometheus metrics
        'prometheus-api-client==0.5.1',  # clusterbuster && prometheus metrics
        'pandas',  # required latest
        'paramiko==3.4.0',
        'PyGitHub==1.55',  # update secrets
        'PyYAML==6.0.1',
        'setuptools',  # for python3.12
        'sphinx==5.0.0',  # readthedocs
        'sphinx-rtd-theme==1.0.0',  # readthedocs
        'tenacity==8.0.1',  # retry decorator
        'tqdm==4.66.3',  # for jupyterlab download file
        'typeguard==2.12.1',
        'typing==3.7.4.3',
        # must add new package inside requirements.txt
    ],

    setup_requires=['pytest', 'pytest-runner', 'wheel', 'coverage'],

    include_package_data=True,

    # dependency_links=[]
)
