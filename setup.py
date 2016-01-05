from setuptools import setup

setup(
    name='wio_cli',
    version='0.1',
    py_modules=['wio'],
    include_package_data=True,
    install_requires=[
        'click',
        'requests',
        'storm'
    ],
    entry_points='''
        [console_scripts]
        wio=wio:cli
    ''',
)
