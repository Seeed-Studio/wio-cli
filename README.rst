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

<!--Configuration
=============

The CLI is configured via environment variables and command-line
options as listed in  http://docs.openstack.org/developer/python-openstackclient/authentication.html.

Authentication using username/password is most commonly used::

   export OS_AUTH_URL=<url-to-openstack-identity>
   export OS_PROJECT_NAME=<project-name>
   export OS_USERNAME=<username>
   export OS_PASSWORD=<password>  # (optional)

The corresponding command-line options look very similar::

   --os-auth-url <url>
   --os-project-name <project-name>
   --os-username <username>
   [--os-password <password>]

If a password is not provided above (in plaintext), you will be interactively
prompted to provide one securely.

Authentication may also be performed using an already-acquired token
and a URL pointing directly to the service API that presumably was acquired
from the Service Catalog::

    export OS_TOKEN=<token>
    export OS_URL=<url-to-openstack-service>

The corresponding command-line options look very similar::

    --os-token <token>
    --os-url <url-to-openstack-service>-->
