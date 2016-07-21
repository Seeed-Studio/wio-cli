import os
import sys
import posixpath
import json
import socket
from . import termui
import click
import requests
import signal
from requests.packages.urllib3.exceptions import InsecureRequestWarning
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


version = '0.2.1'

WIO_LINK_V1_0 = 'Wio Link v1.0'
WIO_NODE_V1_0 = 'Wio Node v1.0'
boards = [WIO_LINK_V1_0, WIO_NODE_V1_0]

login_endpoint = "/v1/user/login"
ext_user_endpoint = "/v1/ext_users"
node_list_endpoint = "/v1/nodes/list"
well_known_endpoint = "/v1/node/.well-known"
nodes_create_endpoint = "/v1/nodes/create"
nodes_rename_endpoint = "/v1/nodes/rename"
nodes_delete_endpoint = "/v1/nodes/delete"
node_resources_endpoint = "/v1/node/resources"

verify = False

CONTEXT_SETTINGS = dict(auto_envvar_prefix='WIO')

class Wio(object):

    def __init__(self):
        # self.home = home
        self.config = {}
        # self.verbose = False

    def set_config(self, key, value):
        self.config[key] = value
        # cur_dir = os.path.split(os.path.realpath(__file__))[0]
        cur_dir = os.path.abspath(os.path.expanduser("~/.wio"))
        db_file_path = '%s/config.json' % cur_dir
        open("%s/config.json"%cur_dir,"w").write(json.dumps(self.config))
        # if self.verbose:
        #     click.echo('config[%s] = %s' % (key, value), file=sys.stderr)


pass_wio = click.make_pass_decorator(Wio, ensure=True)
cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),'commands'))


class ComplexCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and \
               filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__('wio.commands.cmd_' + name,
                             None, None, ['cli'])
        except ImportError:
            return
        return mod.cli


def sigint_handler(signum, frame):
    click.echo()
    exit(0)

@click.command(cls=ComplexCLI, context_settings=CONTEXT_SETTINGS)
@click.version_option(version)
@click.pass_context
def cli(ctx):
    """\b
    Welcome to the Wio Command line utility!
    https://github.com/Seeed-Studio/wio-cli

    For more information Run: wio <command_name> --help
    """
    ctx.obj = Wio()
    cur_dir = os.path.abspath(os.path.expanduser("~/.wio"))
    if not os.path.exists(cur_dir):
        text = {"email":"", "token":""}
        os.mkdir(cur_dir)
        open("%s/config.json"%cur_dir,"w").write(json.dumps(text))
    db_file_path = '%s/config.json' % cur_dir
    config = json.load(open(db_file_path))
    ctx.obj.config = config

    signal.signal(signal.SIGINT, sigint_handler)

    if not verify:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def choise_server(wio):
    while True:
        click.echo("1.) Global Server (New)[https://us.wio.seeed.io]")
        click.echo("2.) Global Server (Old)[https://iot.seeed.cc]")
        click.echo("3.) Chinese Server [https://cn.wio.seeed.io]")
        click.echo("4.) Customize Server")
        click.secho('? ', fg='green', nl=False)
        server = click.prompt(click.style('Please choice server', bold=True), type=int)
        if server == 1:
            wio.set_config("mserver","https://us.wio.seeed.io")
            wio.set_config("server","Global")
            wio.set_config("mserver_ip","54.186.73.152")
            return
        elif server == 2:
            wio.set_config("mserver","https://iot.seeed.cc")
            wio.set_config("server","Global")
            wio.set_config("mserver_ip","45.79.4.239")
            return
        elif server == 3:
            wio.set_config("mserver","https://cn.wio.seeed.io")
            wio.set_config("server","Chinese")
            wio.set_config("mserver_ip","120.25.216.117")
            return
        elif server == 4:
            wio.set_config("server","Customize")
            break
        else:
            click.echo(click.style('>> ', fg='red') + "invalid input.")
            continue

    while 1:
        click.secho('? ', fg='green', nl=False)
        mserver = click.prompt(click.style("Please enter Customize Server url\n(e.g. https://us.wio.seeed.cc or http://192.168.1.10:8080)", bold=True))
        try:
            hostname = urlparse(mserver).hostname
            mserver_ip = socket.gethostbyname(hostname)
            break
        except (IndexError, TypeError):
            click.secho(">> url is not correct format!", fg='red')
            continue
        except Exception as e:
            click.secho(">> %s" %e, fg='red')
            continue

    wio.set_config("mserver", mserver)
    wio.set_config("mserver_ip", mserver_ip)
