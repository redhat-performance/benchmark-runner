
from codecs import open
from os import path
from setuptools import setup, find_packages


__version__ = '1.0.386'


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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],

    zip_safe=False,

    # Find all packages (__init__.py)
    packages=find_packages(include=['benchmark_runner', 'benchmark_runner.*']),

    install_requires=[
        'attrs==21.4.0', # readthedocs
        'azure==4.0.0',
        'boto3==1.20.24',  # s3
        'botocore==1.23.24',  # s3
        'cryptography==36.0.2',  # Remove once https://github.com/paramiko/paramiko/issues/2038 gets fixed.
        'elasticsearch==7.16.1',
        'elasticsearch_dsl==7.4.0',  # for deep search
        'jinja2==3.0.3',
        'myst-parser==0.17.0',  # readthedocs
        'openshift-client==1.0.17',  # clusterbuster && prometheus metrics
        'prometheus-api-client==0.5.1',  # clusterbuster && prometheus metrics
        'pandas',  # required latest
        'paramiko==2.10.1',
        'PyGitHub==1.55',  # update secrets
        'PyYAML==6.0',
        'sphinx==4.5.0',  # readthedocs
        'sphinx-rtd-theme==1.0.0',  # readthedocs
        'tenacity==8.0.1',  # retry decorator
        'typeguard==2.12.1',
        'typing==3.7.4.3',
        # must add new package inside requirements.txt
    ],

    setup_requires=['pytest', 'pytest-runner', 'wheel', 'coverage'],

    include_package_data=True,

    # dependency_links=[]
)
