===============================
Wio Link Command Line Interface
===============================

.. image:: https://img.shields.io/badge/pypi-0.0.14-orange.svg
    :target: https://pypi.python.org/pypi/wio-cli/
    :alt: Latest Version
    
Getting Started
===============

Wio Link Client can be installed from PyPI using pip::

    pip install wio-cli

A list of global options and supported, commands is shown with ``--help``::

    wio --help

More info, that can be used to get help text for a specific command::

    wio <command> --help

Command
==========
Login with your Wiolink account::

    wio login
	
Login state::

    wio state
    
    example:
    $ wio state
    email: xxx@xxx.xx
    token: 4LxiwvwFAw3C7LiiUQiZh6qOj44tV6KGsXyjp3jVzxx
    mserver: https://iot.seeed.cc
    mserver_ip: 45.79.4.239

Displays a list of your devices and their APIs::

    wio list
    
    example:
    $ wio list
	|-- home (online)                                                                
	    |-- sn: e3d0dccd4587f40a5d6ffda236755aa4
	    |-- token: ce140e79f24717ed7d6d44bfb5d848b2
	    |-- resource url: http://192.168.21.115:8080/v1/node/resources?access_token=ce140e79f24717ed7d6d44bfb5d848b2
	    |-- well_known: 
	        |-- GET /v1/node/GroveTempHumProD0/humidity -> float humidity
	        |-- GET /v1/node/GroveTempHumProD0/temperature -> float celsius_degree
	        |-- GET /v1/node/GroveTempHumProD0/temperature_f -> float fahrenheit_degree

Request api, return json::

    wio call <token> <method> <endpoint>
    
    example: 
    $ wio call c74a110c2e397823f0ce53ef669d5b7f  GET /v1/node/GroveMoistureA0/moisture
    {u'moisture': 0}
    
Add a new device with USB connect::
	
    wio setup

config your main server::
	
    wio config mserver

