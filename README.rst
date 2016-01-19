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

call api::

    wio call <token> <method> <endpoint>
    
    example: wio call c74a110c2e397823f0ce53ef669d5b7f  GET /v1/node/GroveMoistureA0/moisture
    {u'moisture': 0}
    
configure with usb connect::
	
    wio setup

config main server::
	
    wio config mserver

