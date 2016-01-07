from setuptools import setup, find_packages

print "wangteng"
setup(
    name='wio-cli',
    version='0.0.4',
    description='CLI for Wio Link',
    url='https://github.com/awong1900/wio_cli',
    author='Ten Wong',
    author_email='wangtengoo7@gmail.com',
    license='MIT',
    packages=['wio'],
    package_data={
        'wio': ['config.json'],
    },
    # data_files=[('config', ['wio/config.json'])],
    # include_package_data=True,
    install_requires=[
        'click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        wio=wio.wio:cli
    ''',
)
