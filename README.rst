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
    
    example:
    $ wio state
    email: xxx@xxx.xx
    token: 4LxiwvwFAw3C7LiiUQiZh6qOj44tV6KGsXyjp3jVzxx
    mserver: https://iot.seeed.cc
    mserver_ip: 45.79.4.239

list wio & apis::

    wio list
    
    example:
    $ wio list
    <wio-cli> sn[7bb5f63b86de785a7fb8243bc7160dca],token[26cda37ff879cd9df93107ed1983aa89] is offline
    <sw> sn[95c5c5d2bb1e82f6ccdef080c6a1275d],token[ddb4d188352bac33d294f04cc9f02355] is offline
    <windows-test> sn[88acb36fada20050c3ce086188a53577],token[c74a110c2e397823f0ce53ef669d5b7f] is online
      GET /v1/node/GroveMoistureA0/moisture -> uint16_t moisture
      GET /v1/node/GroveEncoderUART0/position -> int32_t position
      POST /v1/node/GroveEncoderUART0/reset_position/{int32_t position}
      POST /v1/node/GroveEncoderUART0/enable_acceleration/{uint8_t enable}
      Event GroveEncoderUART0 encoder_position

call api::

    wio call <token> <method> <endpoint>
    
    example: 
    $ wio call c74a110c2e397823f0ce53ef669d5b7f  GET /v1/node/GroveMoistureA0/moisture
    {u'moisture': 0}
    
configure with usb connect::
	
    wio setup

config main server::
	
    wio config mserver

