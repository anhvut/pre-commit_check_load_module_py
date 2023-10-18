import sys
from setuptools import find_packages
from setuptools import setup

install_requires = []
if sys.version_info < (3, 9):
    raise Exception('Need at least python 3.9')


setup(
    name='pre-commit_check_load_module_py',
    description='A pre-commit hook that just loads python module.',
    url='https://github.com/anhvut/pre-commit_check_load_module_py',
    version='0.0.7',

    author='Anh-Vu Tran',
    author_email='anhvutran1@gmail.com',

    platforms='linux',
    classifiers=[
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
    ],

    packages=find_packages('.', exclude=('tests*', 'testing*')),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'check-load-module-py = pre_commit_hook.check_load_module:main',
        ],
    },
)
