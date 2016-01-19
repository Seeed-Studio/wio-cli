===============================
Wio Link Command Line Interface
===============================

.. image:: https://img.shields.io/badge/pypi-0.0.9-orange.svg
    :target: https://pypi.python.org/pypi/wio-cli/
    :alt: Latest Version
    
Getting Started
===============

Wio Link Client can be installed from PyPI using pip::

    pip install wio-cli

There are a few variants on getting help.  A list of global options and supported
commands is shown with ``--help``::

   wio --help

Command
==========
login in::

    wio login
	
get login state::

    wio state

list wio & apis::

   wio list

configure with usb connect::
	
    wio setup

config main server::
	
    wio config mserver
