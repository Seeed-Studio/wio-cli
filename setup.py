from setuptools import setup, find_packages
import re
import os

version = ''
with open('wio/wio.py', 'r') as fd:
    version = re.search(r'^version\s*=\s*[\'"]([^\'"]*)[\'"]',
                    fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='wio-cli',
    version=version,
    description='Command line for Wio Link',
    url='https://github.com/Seeed-Studio/wio-cli',
    author='Ten Wong',
    author_email='wangtengoo7@gmail.com',
    license='MIT',
    packages=['wio', 'wio.commands'],
    # data_files=[('config', ['wio/config.json'])],
    # include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'pyserial',
    ],
    entry_points='''
        [console_scripts]
        wio=wio.wio:cli
    ''',
)
