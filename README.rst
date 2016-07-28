===============================
Wio Link Command Line Toolset
===============================

.. image:: https://img.shields.io/badge/pypi-0.3.0-green.svg
    :target: https://pypi.python.org/pypi/wio-cli/
    :alt: Latest Version

CLI is used to add WioLink and WioNode, list the Wio device and so on.

Getting Started
===============
**Note:** If can't find the USB device, should be install USB to Serial driver first, `download here`_

.. _download here: https://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx

Wio Link Client can be installed from PyPI using pip::

    $ pip install wio-cli

On Python3, use virtualenv to install::

    $ virtualenv -p python2 env2
    $ source env2/bin/activate
    $ pip install wio-cli
    $ wio --version

    
If you have already installed the library, execute the following command to ensure you’re using the latest library::

    pip install wio-cli --upgrade

A list of global options and supported, commands is shown with ``--help``::

    $ wio --help

More info, that can be used to get help text for a specific command::

    $ wio <command> --help

Getting Started with Wio Link Command Line Toolset: http://www.seeedstudio.com/recipe/1136-getting-started-with-wio-link-command-line-toolset.html)

Command
==========
Login with your Wiolink account::

    $wio login

Add a new device with USB connect::

    $ wio setup
        
Login state::

    $ wio state

    example:
    $ wio state
    email: xxx@xxx.xx
    token: 4LxiwvwFAw3C7LiiUQiZh6qOj44tV6KGsXyjp3jVzxx
    mserver: https://iot.seeed.cc
    mserver_ip: 45.79.4.239

Displays a list of your devices and their APIs::

    $ wio list

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

    $ wio call <token> <method> <endpoint>

    example:
    $ wio call c74a110c2e397823f0ce53ef669d5b7f  GET /v1/node/GroveMoistureA0/moisture
    {u'moisture': 0}


Delete a device::

    $ wio delete <device_sn>

    example:
    $wio delete 2885b2cab8abc5fb8e229e4a77bf5e4d
    >> Delete device commplete!

Config your device setting::

    $wio config --debug [on|off], enable/disable wio debug
    $wio config --get-debug, get wio debug status

Serial port permissions
==========
1. now as normal user from terminal:

    $ ls -l /dev/ttyUSB*

you will get something like:

    crw-rw---- 1 root dialout 188, 0 5 apr 23.01 ttyUSB0

The "0" might be a different number, or multiple entries might be returned. In the first case the data we need is "uucp", in the second "dialout" (is the group owner of the file.

2. Now we just need to add our user to the group:

    $ sudo usermod -a -G group-name username

where group-name is the data found before, and username is your linux user name. You will need to log out and in again for this change to take effect. such as:

    $ sudo usermod -a -G dialout tengwang
