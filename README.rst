===============================
Wio Link Command Line Interface
===============================

.. image:: https://img.shields.io/pypi/v/python-openstackclient.svg
    :target: https://pypi.python.org/pypi/python-openstackclient/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/dm/python-openstackclient.svg
    :target: https://pypi.python.org/pypi/python-openstackclient/
    :alt: Downloads

Getting Started
===============

Wio Link Client can be installed from PyPI using pip::

    pip install wio-cli

There are a few variants on getting help.  A list of global options and supported
commands is shown with ``--help``::

   wio --help

<!--There is also a ``help`` command that can be used to get help text for a specific
command::

    openstack help
    openstack help server create-->
    
    
Command
==========
login in:

	wio login
	
get login state:

	wio state
	
list wio & apis:

	wio list

configure with usb connect:
	
	wio setup

config main server:
	
	wio config mserver
