from setuptools import setup, find_packages

setup(
    name='wio-cli',
    version='0.0.14',
    description='CLI for Wio Link',
    url='https://github.com/Seeed-Studio/wio-cli',
    author='Ten Wong',
    author_email='wangtengoo7@gmail.com',
    license='MIT',
    packages=['wio'],
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
