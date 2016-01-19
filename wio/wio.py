import os
import sys
import posixpath
import json
import time
# import glob
import serial
import serial_list
import termui

import click
import requests

# from serial_list
# api_prefix = "http://192.168.21.48:8080"
# api_prefix = "https://iot.seeed.cc"
login_endpoint = "/v1/user/login"
node_list_endpoint = "/v1/nodes/list"
well_known_endpoint = "/v1/node/.well-known"
nodes_create_endpoint = "/v1/nodes/create"
nodes_rename_endpoint = "/v1/nodes/rename"
nodes_delete_endpoint = "/v1/nodes/delete"

class Wio(object):

    def __init__(self):
        # self.home = home
        self.config = {}
        self.verbose = False

    def set_config(self, key, value):
        self.config[key] = value
        # cur_dir = os.path.split(os.path.realpath(__file__))[0]
        cur_dir = os.path.abspath(os.path.expanduser("~/.wio"))
        db_file_path = '%s/config.json' % cur_dir
        open("%s/config.json"%cur_dir,"w").write(json.dumps(self.config))
        if self.verbose:
            click.echo('config[%s] = %s' % (key, value), file=sys.stderr)

    def __repr__(self):
        return '<Wio %r>' % self.home


pass_wio = click.make_pass_decorator(Wio, ensure=True)


@click.group()
# @click.option('--wio-home', envvar='REPO_HOME', default='.wio',
#               metavar='PATH', help='Changes the wiository folder location.')
# @click.option('--config', nargs=2, multiple=True,
#               metavar='KEY VALUE', help='Overrides a config key/value pair.')
@click.option('--verbose', '-v', is_flag=True,
              help='Enables verbose mode.')
@click.version_option('0.0.9')
@click.pass_context
def cli(ctx, verbose):
    """Wio is a command line tool that showcases how to build complex
    command line interfaces with Click.

    This tool is supposed to look like a distributed version control
    system to show how something like this can be structured.
    """
    # Create a wio object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_wio decorator.
    ctx.obj = Wio()
    ctx.obj.verbose = verbose
    # config.json
    # cur_dir = os.path.split(os.path.realpath(__file__))[0]
    cur_dir = os.path.abspath(os.path.expanduser("~/.wio"))
    if not os.path.exists(cur_dir):
        text = {"email":"", "token":""}
        os.mkdir(cur_dir)
        open("%s/config.json"%cur_dir,"w").write(json.dumps(text))
    db_file_path = '%s/config.json' % cur_dir
    config = json.load(open(db_file_path))
    ctx.obj.config = config

def login_server(wio):
    while True:
        click.echo("1.) International[https://iot.seeed.cc]")
        click.echo("2.) China[https://cn.iot.seeed.cc]")
        click.echo("3.) Local")
        server = click.prompt("choice main server", type=int)
        if server == 1:
            wio.set_config("mserver","https://iot.seeed.cc")
            wio.set_config("mserver_ip","45.79.4.239")
            return
        elif server == 2:
            wio.set_config("mserver","https://cn.iot.seeed.cc")
            wio.set_config("mserver_ip","120.25.216.117")
            return
        elif server == 3:
            break
        else:
            continue

    click.secho('> ', fg='green', nl=False)
    mserver_ip = click.prompt("Please enter local main server ip")

    click.secho('> ', fg='green', nl=False)
    mserver = click.prompt("Please enter local main server url")

    wio.set_config("mserver", mserver)
    wio.set_config("mserver_ip", mserver_ip)

@cli.command()
# @click.option('--mserver', callback=login_server, expose_value=False, help='The developer\'s email address', is_eager=True)
# @click.option('--email', prompt='Please enter your email address', help='The developer\'s email address')
# @click.option('--password', prompt='Please enter your password', hide_input=True, help='The login password.')
@pass_wio
def login(wio):
    '''login with your wio link account'''
    mserver = wio.config.get("mserver", None)
    if mserver:
        click.echo(click.style('> ', fg='green') + "Current main server is: " +
            click.style(mserver, fg='green'))

    if click.confirm(click.style('Would you like log in with a different main server?', bold=True), default=False):
        login_server(wio)

    email = click.prompt(click.style('? ', fg='green') +
        click.style('Please enter your email address', bold=True), type=str)
    password = click.prompt(click.style('? ', fg='green') +
        click.style('Please enter your password', bold=True), hide_input=True, type=str)

    thread = termui.waiting_echo("Sending login details...")
    thread.start()
    params = {"email":email, "password":password}
    api_prefix = wio.config.get("mserver", None)
    r = requests.post("%s%s" %(api_prefix, login_endpoint), params=params)
    token = r.json().get("token", None)
    wio.set_config('email', email)
    wio.set_config('token', token)
    if token:
        thread.stop('')
        thread.join()
        click.secho("\r> ", fg='green', nl=False)
        click.echo("Successfully completed login!")
    else:
        thread.stop('')
        thread.join()
        error = r.json().get("error", None)
        if not error:
            error = r.json().get("msg", None)
        click.secho("\r>> ", fg='red', nl=False)
        click.echo('%s' %error)

@cli.command()
@pass_wio
def list(wio):
    '''List WioLinks and API'''
    user_token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not user_token:
        click.echo(click.style('>>', fg='red') + "Please login, use " +
            click.style("wio login", fg='green'))
        return

    thread = termui.waiting_echo("Retrieving devices...")
    thread.start()
    params = {"access_token":user_token}
    r = requests.get("%s%s" %(api_prefix, node_list_endpoint), params=params, timeout=10)
    json_response = None
    json_response = r.json()
    if not json_response:
        pass
        click.echo("error")
        return
    nodes = json_response.get("nodes", None)
    thread.message("Retrieving device APIs...")
    nodes_api = []
    for n in nodes:
        if n['name'] == 'node000':
            params = {"access_token":user_token, "node_sn":n['node_sn']}
            r = requests.post("%s%s" %(api_prefix, nodes_delete_endpoint), params=params, timeout=10)
            json_response = None
            json_response = r.json()
            if not json_response:
                click.echo("error")
            continue
        if n["online"]:
            params = {"access_token":n["node_key"]}
            r = requests.get("%s%s" %(api_prefix, well_known_endpoint), params=params, timeout=10)
            json_response = None
            json_response = r.json()
            if not json_response:
                click.echo("error")
            apis = json_response["well_known"]
            n['apis'] = apis
        else:
            n['apis'] = []
        nodes_api.append(n)

    thread.stop('')
    thread.join()

    for n in nodes_api:
        if n['online']:
            onoff = 'online'
            fg = "green"
        else:
            onoff = 'offline'
            fg = "cyan"
        click.secho("  <%s>" %n['name'], fg=fg, nl=False)
        click.echo(" sn[%s],token[%s] is %s" %(n["node_sn"], n["node_key"], onoff))
        for api in n['apis']:
            click.echo("    " + api)

@cli.command()
@click.argument('token')
@click.argument('method')
@click.argument('endpoint')
@click.option('--xchange', help='xchange server url')
@pass_wio
def call(wio, method, endpoint, token, xchange):
    '''
    request api test, return json.
    example: wio call 98dd464bd268d4dc4cb9b37e4e779313 GET /v1/node/GroveTempHumProD0/temperature
    '''
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix:
        click.echo("Please login [wio login]")
        return
    api = "%s%s?access_token=%s" %(api_prefix, endpoint, token)
    # print api
    if method == "GET":
        r = requests.get(api)
    elif method == "POST":
        r = requests.post(api)
    else:
        click.echo("API method [%s] is wrong, should be GET or POST." %method)
        return
    try:
        click.echo(r.json())
    except Exception as e:
        click.echo("Error[%s], API[%s]" %(e, api))

@cli.command()
@pass_wio
def state(wio):
    '''login state'''
    email = wio.config.get("email",None)
    mserver = wio.config.get("mserver",None)
    mserver_ip = wio.config.get("mserver_ip",None)
    token = wio.config.get("token",None)
    click.echo("email: %s" %email)
    click.echo("token: %s" %token)
    click.echo("mserver: %s" %mserver)
    click.echo("mserver_ip: %s" %mserver_ip)

@cli.command()
@click.argument('subcommand')
# @click.argument('sdf')
# @click.option('--mserver', default= None, help='Set main server ip, such as 192.168.21.48')
@pass_wio
def config(wio, subcommand):
    '''
    subcommand: mserver
    '''
    if subcommand == "mserver":
        while True:
            click.echo("1.) International[https://iot.seeed.cc]")
            click.echo("2.) China[https://cn.iot.seeed.cc]")
            click.echo("3.) Local")
            server = click.prompt("choice main server", type=int)
            if server == 1:
                wio.set_config("mserver","https://iot.seeed.cc")
                wio.set_config("mserver_ip","45.79.4.239")
                return
            elif server == 2:
                wio.set_config("mserver","https://cn.iot.seeed.cc")
                wio.set_config("mserver_ip","120.25.216.117")
                return
            elif server == 3:
                break
            else:
                continue

        click.secho('> ', fg='green', nl=False)
        mserver_ip = click.prompt("Please enter local main server ip")

        click.secho('> ', fg='green', nl=False)
        mserver = click.prompt("Please enter local main server url")

        wio.set_config("mserver", mserver)
        wio.set_config("mserver_ip", mserver_ip)

@cli.command()
@pass_wio
def setup(wio):
    click.secho('> ', fg='green', nl=False)
    click.echo("Setup is easy! Let's get started...\n")
    click.secho('! ', fg='green', nl=False)
    click.echo("PROTIP: " +
        click.style("Hold the ", fg='white') +
        click.style("Configure ", fg='green') +
        click.style("button ~4s into Configure Mode!", fg='white'))
    click.secho('! ', fg='green', nl=False)
    click.echo("PROTIP: " +
        click.style("Please make sure you are ", fg='white') +
        click.style("connected ", fg='green') +
        click.style("to the ", fg='white') +
        click.style("main server", fg='green'))
    click.echo()
    click.secho('? ', fg='green', nl=False)
    if not click.confirm(click.style('Would you like continue?', bold=True), default=True):
        click.echo('Quit setup!')
        return

    token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not token:
        click.echo("Please login [wio login]")
        return
    params = {"name":"node000","access_token":token}
    r = requests.post("%s%s" %(api_prefix, nodes_create_endpoint), params=params)
    json_response = r.json()

    node_key = json_response["node_key"]
    node_sn = json_response["node_sn"]

    # list serial
    ports = serial_list.serial_ports()
    # click.echo(ports)
    count = len(ports)
    port = None
    if count == 0:
        pass #scan
    elif count == 1:
        port = ports[0]
    elif count >= 2:
        while 1:
            for x in range(len(ports)):
                click.echo("%s.) %s" %(x, ports[x]))
            click.secho('? ', fg='green', nl=False)
            value = click.prompt(click.style('Please choice a device', bold=True), type=int)
            if value >= 0 and value <= len(ports):
                port = ports[value]
                break
            else:
                click.echo(click.style('>> ', fg='red') + "invalid input.")

    if not port:
        click.echo("No connect device!")
        return
    click.echo(click.style('> ', fg='green') +
        "I have detected a " +
        click.style("Wiolink ", fg='green') +
        "connected via USB.")

    while 1:
        ap = click.prompt(click.style('> ', fg='green') +
            click.style('Please enter the SSID of your Wi-Fi network', bold=True), type=str)
        ap_pwd = click.prompt(click.style('> ', fg='green') +
            click.style('Please enter your Wi-Fi network password (leave blank for none)', bold=True),
            default='', show_default=False)
        d_name = click.prompt(click.style('> ', fg='green') +
        click.style('Please enter the name of a device will be created', bold=True), type=str)

        msvr = wio.config.get("mserver", None)
        click.echo(click.style('> ', fg='green') + "Here's what we're going to send to the Wiolink:")
        click.echo()
        # click.echo(click.style(' - ', fg='green') + "main server: %s" %msvr)
        click.echo(click.style('> ', fg='green') + "Wi-Fi network: " +
            click.style(ap, fg='green'))
        ap_pwd_p = ap_pwd
        if ap_pwd_p == '':
            ap_pwd_p = 'None'
        click.echo(click.style('> ', fg='green') + "Password: " +
            click.style(ap_pwd_p, fg='green'))
        click.echo(click.style('> ', fg='green') + "Device name: " +
            click.style(d_name, fg='green'))
        click.echo()

        if click.confirm(click.style('? ', fg='green') +
            "Would you like to continue with the information shown above?", default=True):
            break
    click.echo()
    #waiting ui
    thread = termui.waiting_echo("Sending Wi-Fi information to device...")
    thread.start()

    # send serial command
    msvr_ip = wio.config.get("mserver_ip", None)
    xsvr_ip = msvr_ip
    send_flag = False
    while 1:
        with serial.Serial(port, 115200, timeout=10) as ser:
            cmd = "APCFG: %s\t%s\t%s\t%s\t%s\t%s\t\r\n" %(ap, ap_pwd, node_key, node_sn, msvr_ip, xsvr_ip)
            # click.echo(cmd)
            ser.write(cmd.encode('utf-8'))
            # while True:
            if "ok" in ser.readline():
                click.echo(click.style('\r> ', fg='green') + "Send Wi-Fi information to device success.")
                thread.message("The Wiolink now attempt to connect to main server...")
                send_flag = True
        if send_flag:
            break

    token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not token:
        click.echo("Please login [wio login]")
        return

    # click.echo(json_response)
    state_online = False
    for i in range(30):
        params = {"access_token":token}
        r = requests.get("%s%s" %(api_prefix, node_list_endpoint), params=params)
        json_response = r.json()
        for n in json_response["nodes"]:
            if n["node_sn"] == node_sn and n["online"]:
                click.echo(click.style('\r> ', fg='green') + "The Wiolink connect to main server success.         ")
                thread.message("Setting Wiolink name...")
                state_online = True
                break
        if state_online:
            break
        time.sleep(1)

    if not state_online:
        click.echo(click.style('\r>> ', fg='red') + "The Wiolink connect to main server failure.")
        thread.stop('')
        return

    params = {"name":d_name,"node_sn":node_sn,"access_token":token}
    r = requests.post("%s%s" %(api_prefix, nodes_rename_endpoint), params=params)
    json_response = r.json()
    # click.echo(json_response)
    if json_response.get("result", None) == "ok":
        click.echo(click.style('\r> ', fg='green') + "Set Wiolink name success.")
    else:
        click.echo(click.style('\r>> ', fg='red') + "Set Wiolink name failure.")
        thread.stop('')
        return

    thread.stop('')
    thread.join()
    click.echo()
    click.echo(click.style('> ', fg='green') +
        click.style("Configuration complete!", fg='white', bold=True))


# @cli.command()
# def test():
#     value = click.prompt('Enter one more', default='', show_default=False)
