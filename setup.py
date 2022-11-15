from setuptools import setup

setup(
    name='fpds',
    version='0.1',
    py_modules=['fpds'],
    install_requires=[
        'Click',
        'requests'
    ],
    entry_points={'console_scripts': ["fpds=src.fpds.cli:cli"]}
)