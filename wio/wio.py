import os
import sys
import posixpath
import json
import time
# import glob
import serial
from . import serial_list
from . import termui

import click
import requests
import signal
from requests.packages.urllib3.exceptions import InsecureRequestWarning

version = '0.0.30'

login_endpoint = "/v1/user/login"
node_list_endpoint = "/v1/nodes/list"
well_known_endpoint = "/v1/node/.well-known"
nodes_create_endpoint = "/v1/nodes/create"
nodes_rename_endpoint = "/v1/nodes/rename"
nodes_delete_endpoint = "/v1/nodes/delete"
node_resources_endpoint = "/v1/node/resources"

verify = False

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

def sigint_handler(signum, frame):
    click.echo()
    exit(0)

@click.group()
# @click.option('--wio-home', envvar='REPO_HOME', default='.wio',
#               metavar='PATH', help='Changes the wiository folder location.')
# @click.option('--config', nargs=2, multiple=True,
#               metavar='KEY VALUE', help='Overrides a config key/value pair.')
# @click.option('--verbose', '-v', is_flag=True,
#               help='Enables verbose mode.')
@click.version_option(version)
@click.pass_context
def cli(ctx):
    """\b
    Welcome to the Wiolink Command line utility!
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

def login_server(wio):
    while True:
        click.echo("1.) International[https://iot.seeed.cc]")
        click.echo("2.) China[https://cn.iot.seeed.cc]")
        click.echo("3.) Local")
        click.secho('? ', fg='green', nl=False)
        server = click.prompt(click.style('Please choice main server', bold=True), type=int)
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
            click.echo(click.style('>> ', fg='red') + "invalid input.")
            continue

    click.secho('? ', fg='green', nl=False)
    mserver_ip = click.prompt(click.style('Please enter local main server ip', bold=True))

    click.secho('? ', fg='green', nl=False)
    mserver = click.prompt(click.style("Please enter local main server url(e.g. https://192.168.31.2)", bold=True))

    wio.set_config("mserver", mserver)
    wio.set_config("mserver_ip", mserver_ip)

@cli.command()
@pass_wio
def login(wio):
    '''
    Login with your Wiolink account.

    \b
    DOES:
        Login and save an access token for interacting with your account on the Wiolink.

    \b
    USE:
        wio login
    '''
    mserver = wio.config.get("mserver", None)
    if mserver:
        click.echo(click.style('> ', fg='green') + "Current main server is: " +
            click.style(mserver, fg='green'))
        if click.confirm(click.style('Would you like log in with a different main server?', bold=True), default=False):
            login_server(wio)
    else:
        login_server(wio)
    email = click.prompt(click.style('? ', fg='green') +
        click.style('Please enter your email address', bold=True), type=str)
    password = click.prompt(click.style('? ', fg='green') +
        click.style('Please enter your password', bold=True), hide_input=True, type=str)

    thread = termui.waiting_echo("Sending login details...")
    thread.daemon = True
    thread.start()
    params = {"email":email, "password":password}
    api_prefix = wio.config.get("mserver", None)
    try:
        r = requests.post("%s%s" %(api_prefix, login_endpoint), params=params, timeout=10, verify=verify)
        r.raise_for_status()
        json_response = r.json()
    except requests.exceptions.HTTPError as e:
        thread.stop('')
        thread.join()
        if r.status_code == 400:
            error = r.json().get("error", None)
            click.secho(">> %s" %error, fg='red')
        else:
            click.secho(">> %s" %e, fg='red')
        return
    except Exception as e:
        thread.stop('')
        thread.join()
        click.secho(">> %s" %e, fg='red')
        return

    token = json_response.get("token", None)
    wio.set_config('email', email)
    wio.set_config('token', token)

    thread.stop('')
    thread.join()
    click.secho("\r> ", fg='green', nl=False)
    click.echo("Successfully completed login!")

@cli.command()
@pass_wio
def list(wio):
    '''
    Displays a list of your devices.

    \b
    DOES:
        Displays a list of your devices, as well as their APIs

    \b
    USE:
        wio list
    '''
    user_token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not user_token:
        click.echo(click.style('>> ', fg='red') + "Please login, use " +
            click.style("wio login", fg='green'))
        return

    thread = termui.waiting_echo("Retrieving devices...")
    thread.daemon = True
    thread.start()
    params = {"access_token":user_token}
    try:
        r = requests.get("%s%s" %(api_prefix, node_list_endpoint), params=params, timeout=10, verify=verify)
        r.raise_for_status()
        json_response = r.json()
    except requests.exceptions.HTTPError as e:
        thread.stop('')
        thread.join()
        if r.status_code == 400:
            error = r.json().get("error", None)
            click.secho(">> %s" %error, fg='red')
        else:
            click.secho(">> %s" %e, fg='red')
        return
    except Exception as e:
        thread.stop('')
        thread.join()
        click.secho(">> %s" %e, fg='red')
        return

    nodes = json_response.get("nodes", None)
    thread.message("Retrieving device APIs...")
    node_list = []
    for n in nodes:
        if n['name'] == 'node000':
            params = {"access_token":user_token, "node_sn":n['node_sn']}
            try:
                r = requests.post("%s%s" %(api_prefix, nodes_delete_endpoint), params=params, timeout=10, verify=verify)
                r.raise_for_status()
                json_response = r.json()
            except requests.exceptions.HTTPError as e:
                thread.stop('')
                thread.join()
                if r.status_code == 400:
                    error = r.json().get("error", None)
                    click.secho(">> %s" %error, fg='red')
                else:
                    click.secho(">> %s" %e, fg='red')
                return
            except Exception as e:
                thread.stop('')
                thread.join()
                click.secho(">> %s" %e, fg='red')
                return
            continue
        if n["online"]:
            params = {"access_token":n["node_key"]}
            try:
                r = requests.get("%s%s" %(api_prefix, well_known_endpoint), params=params, timeout=15, verify=verify)
                r.raise_for_status()
                json_response = r.json()
            except requests.exceptions.HTTPError as e:
                # thread.stop('')
                # thread.join()
                if r.status_code == 400:
                    error = r.json().get("error", None)
                    click.secho(">> %s" %error, fg='red')
                else:
                    click.secho(">> %s" %e, fg='red')
                n['well_known'] = []
                # n['onoff'] = 'offline'
            except Exception as e:
                # thread.stop('')
                # thread.join()
                click.secho(">> %s" %e, fg='red')
                n['well_known'] = []
            else:
                well_known = json_response["well_known"] #todo error risk
                n['well_known'] = well_known

            n['onoff'] = 'online'
        else:
            n['well_known'] = []
            n['onoff'] = 'offline'

        n['resources'] = "%s%s?access_token=%s" %(api_prefix, node_resources_endpoint, n['node_key'])
        node_list.append(n)

    thread.stop('')
    thread.join()

    termui.tree(node_list)

@cli.command()
@click.argument('token')
@click.argument('method')
@click.argument('endpoint')
# @click.option('--xchange', help='xchange server url')
@pass_wio
def call(wio, method, endpoint, token,):
    '''
    Request api, return json.

    \b
    DOES:
        Call a api on your devices.
        token: device_token
        method: GET or POST
        endpoint: device_path, such as: /v1/node/GroveTempHumProD0/temperature
        wio call <device_token> <request_method> <device_path>

    \b
    EXAMPLE:
        wio call 98dd464bd268d4dc4cb9b37e4e779313 GET /v1/node/GroveTempHumProD0/temperature
    '''
    user_token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not user_token:
        click.echo(click.style('>> ', fg='red') + "Please login, use " +
            click.style("wio login", fg='green'))
        return

    api = "%s%s?access_token=%s" %(api_prefix, endpoint, token)

    try:
        if method == "GET":
            r = requests.get(api, timeout=15, verify=verify)
        elif method == "POST":
            r = requests.post(api, timeout=15, verify=verify)
        else:
            click.secho(">> METHOD [%s] is wrong, should be GET or POST." %method, fg='red')
            return
        r.raise_for_status()
        json_response = r.json()
    except requests.exceptions.HTTPError as e:
        if r.status_code == 400:
            # error = r.json().get("error", None)
            # click.secho(">> %s" %error, fg='red')
            click.echo(r.json())
        else:
            click.secho(">> %s" %e, fg='red')
        return
    except Exception as e:
        click.secho(">> %s" %e, fg='red')
        return

    click.echo(r.json())

@cli.command()
@pass_wio
def state(wio):
    '''
    Login state.

    \b
    DOES:
        Display login email, token, main server ip and url.

    \b
    USE:
        wio state
    '''
    user_token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not user_token:
        click.echo(click.style('>> ', fg='red') + "Please login, use " +
            click.style("wio login", fg='green'))
        return

    email = wio.config.get("email",None)
    mserver = wio.config.get("mserver",None)
    mserver_ip = wio.config.get("mserver_ip",None)
    token = wio.config.get("token",None)
    click.secho('> ', fg='green', nl=False)
    click.echo("email: " + click.style(email, fg='green', bold=True))
    click.secho('> ', fg='green', nl=False)
    click.echo("token: " + click.style(token, fg='green', bold=True))
    click.secho('> ', fg='green', nl=False)
    click.echo("main server: " + click.style(mserver, fg='green', bold=True))
    click.secho('> ', fg='green', nl=False)
    click.echo("main server ip: " + click.style(mserver_ip, fg='green', bold=True))

@cli.command()
@click.argument('command', metavar='<main-server>')
# @click.option('--mserver', default= None, help='Set main server ip, such as 192.168.21.48')
@pass_wio
def config(wio, command):
    '''
    config your main server and so on.

    \b
    DOES:
        The config command lets you change your setting,
        such as main server

    \b
    EXAMPLE:
        wio config main-server
    '''
    if command == "main-server":
        login_server(wio)

@cli.command()
@pass_wio
def setup(wio):
    '''
    Add a new device with USB connect.

    \b
    DOES:
        Guides you through setting up a new device, and getting it on your network.

    \b
    USE:
        wio setup
    '''
    token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not token:
        click.echo(click.style('>> ', fg='red') + "Please login, use " +
            click.style("wio login", fg='green'))
        return

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

    thread = termui.waiting_echo("Getting message from main server...")
    thread.daemon = True
    thread.start()
    try:
        params = {"name":"node000","access_token":token}
        r = requests.post("%s%s" %(api_prefix, nodes_create_endpoint), params=params, timeout=10, verify=verify)
        r.raise_for_status()
        json_response = r.json()
    except requests.exceptions.HTTPError as e:
        thread.stop('')
        thread.join()
        if r.status_code == 400:
            error = r.json().get("error", None)
            click.secho(">> %s" %error, fg='red')
        else:
            click.secho(">> %s" %e, fg='red')
        return
    except Exception as e:
        thread.stop('')
        thread.join()
        click.secho(">> %s" %e, fg='red')
        return

    thread.stop('')
    thread.join()

    node_key = json_response["node_key"]
    node_sn = json_response["node_sn"]

    # list serial
    try:
        ports = serial_list.serial_ports()
    except serial.SerialException as e:
        click.secho('>> ', fg='red', nl=False)
        click.echo(e)
        if e.errno == 13:
            click.echo("For more information, see https://github.com/Seeed-Studio/wio-cli#serial-port-permissions")
        return
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
            if value >= 0 and value < len(ports):
                port = ports[value]
                break
            else:
                click.echo(click.style('>> ', fg='red') + "invalid input.")

    if not port:
        click.secho('>> ', fg='red', nl=False)
        click.echo("No found device! Plese connect your Wiolink with USB.")
        return
    click.echo(click.style('> ', fg='green') +
        "I have detected a " +
        click.style("Wiolink ", fg='green') +
        "connected via USB.")

    # check is configure mode?
    thread = termui.waiting_echo("Getting device information...")
    thread.daemon = True
    thread.start()

    flag = False
    try:
        with serial.Serial(port, 115200, timeout=5) as ser:
            cmd = 'Blank?\r\n'
            ser.write(cmd.encode('utf-8'))
            if 'Node' in ser.readline():
                flag = True
    except serial.SerialException as e:
        thread.stop('')
        thread.join()
        click.secho('>> ', fg='red', nl=False)
        click.echo(e)
        if e.errno == 13:
            click.echo("For more information, see https://github.com/Seeed-Studio/wio-cli#serial-port-permissions")
        return

    thread.stop('')
    thread.join()

    if flag:
        click.secho('> ', fg='green', nl=False)
        click.secho("Found Wiolink.", fg='green', bold=True)
        click.echo()
    else:
        click.secho('> ', fg='green', nl=False)
        click.secho("No nearby Wiolink detected.", fg='white', bold=True)
        if click.confirm(click.style('? ', fg='green') +
                click.style("Would you like to wait and monitor for Wiolink entering configure mode", bold=True),
                default=True):

            thread = termui.waiting_echo("Waiting for a wild Wiolink to appear... (press ctrl + C to exit)")
            thread.daemon = True
            thread.start()

            flag = False
            while 1:
                with serial.Serial(port, 115200, timeout=5) as ser:
                    cmd = 'Blank?\r\n'
                    ser.write(cmd.encode('utf-8'))
                    if 'Node' in ser.readline():
                        flag = True
                        break

            thread.stop('')
            thread.join()
            click.secho('> ', fg='green', nl=False)
            click.secho("Found Wiolink.", fg='green', bold=True)
            click.echo()
        else:
            click.secho('> ', fg='green', nl=False)
            click.secho("\nQuit wio setup!", bg='white', bold=True)

    while 1:
        if not click.confirm(click.style('? ', fg='green') +
                    click.style("Would you like to manually enter your Wi-Fi network configuration?", bold=True),
                    default=False):
            thread = termui.waiting_echo("Asking the Wiolink to scan for nearby Wi-Fi networks...")
            thread.daemon = True
            thread.start()

            flag = False
            with serial.Serial(port, 115200, timeout=3) as ser:
                cmd = 'SCAN\r\n'
                ser.write(cmd.encode('utf-8'))
                ssid_list = []
                while True:
                    ssid = ser.readline()
                    if ssid == '\r\n':
                        flag = True
                        break
                    ssid = ssid.strip('\r\n')
                    ssid_list.append(ssid)

            if flag:
                thread.stop('')
                thread.join()
            else:
                thread.stop("\rsearch failure...\n")
                return

            while 1:
                for x in range(len(ssid_list)):
                    click.echo("%s.) %s" %(x, ssid_list[x]))
                click.secho('? ', fg='green', nl=False)
                value = click.prompt(
                            click.style('Please select the network to which your Wiolink should connect', bold=True),
                            type=int)
                if value >= 0 and value < len(ssid_list):
                    ssid = ssid_list[value]
                    break
                else:
                    click.echo(click.style('>> ', fg='red') + "invalid input, range 0 to %s" %(len(ssid_list)-1))

            ap = ssid
        else:
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
            click.style(ap, fg='green', bold=True))
        ap_pwd_p = ap_pwd
        if ap_pwd_p == '':
            ap_pwd_p = 'None'
        click.echo(click.style('> ', fg='green') + "Password: " +
            click.style(ap_pwd_p, fg='green', bold=True))
        click.echo(click.style('> ', fg='green') + "Device name: " +
            click.style(d_name, fg='green', bold=True))
        click.echo()

        if click.confirm(click.style('? ', fg='green') +
            "Would you like to continue with the information shown above?", default=True):
            break

    click.echo()
    #waiting ui
    thread = termui.waiting_echo("Sending Wi-Fi information to device...")
    thread.daemon = True
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
        try:
            params = {"access_token":token}
            r = requests.get("%s%s" %(api_prefix, node_list_endpoint), params=params)
            r.raise_for_status()
            json_response = r.json()
        except requests.exceptions.HTTPError as e:
            thread.stop('')
            thread.join()
            if r.status_code == 400:
                error = r.json().get("error", None)
                click.secho(">> %s" %error, fg='red')
            else:
                click.secho(">> %s" %e, fg='red')
            return
        except Exception as e:
            thread.stop('')
            thread.join()
            click.secho(">> %s" %e, fg='red')
            return

        for n in json_response["nodes"]:
            if n["node_sn"] == node_sn and n["online"]:
                click.echo(click.style('\r> ', fg='green') + "The Wiolink connect to main server success.              ")
                thread.message("Setting Wiolink name...")
                state_online = True
                break
        if state_online:
            break

        thread.message("The Wiolink now attempt to connect to main server... [%s]" %(30-i))
        time.sleep(1)

    if not state_online:
        thread.stop('')
        thread.join()
        click.echo(click.style('\r>> ', fg='red') + "The Wiolink connect to main server failure.")
        click.secho("\n> Please check info you enter, Try again.", fg='white', bold=True)

        return

    try:
        params = {"name":d_name,"node_sn":node_sn,"access_token":token}
        r = requests.post("%s%s" %(api_prefix, nodes_rename_endpoint), params=params)
        r.raise_for_status()
        json_response = r.json()
    except requests.exceptions.HTTPError as e:
        thread.stop('')
        thread.join()
        if r.status_code == 400:
            error = r.json().get("error", None)
            click.secho(">> %s" %error, fg='red')
        else:
            click.secho(">> %s" %e, fg='red')
        return
    except Exception as e:
        thread.stop('')
        thread.join()
        click.secho(">> %s" %e, fg='red')
        return
    click.echo(click.style('\r> ', fg='green') + "Set Wiolink name success.")

    thread.stop('')
    thread.join()
    click.echo()
    click.echo(click.style('> ', fg='green') +
        click.style("Configuration complete!", fg='white', bold=True))

@cli.command()
@click.argument('sn')
@pass_wio
def delete(wio, sn):
    '''
    Delete a device.

    \b
    DOES:
        Delete a device.
        sn: device_sn
        wio delete <device_sn>

    \b
    EXAMPLE:
        wio delete 2885b2cab8abc5fb8e229e4a77bf5e4d
    '''
    user_token = wio.config.get("token", None)
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not user_token:
        click.echo(click.style('>> ', fg='red') + "Please login, use " +
            click.style("wio login", fg='green'))
        return

    params = {"access_token":user_token, "node_sn":sn}
    try:
        r = requests.post("%s%s" %(api_prefix, nodes_delete_endpoint), params=params, timeout=10, verify=verify)
        r.raise_for_status()
        json_response = r.json()
    except requests.exceptions.HTTPError as e:
        if r.status_code == 400:
            error = r.json().get("error", None)
            click.secho(">> %s" %error, fg='red')
        else:
            click.secho(">> %s" %e, fg='red')
        return
    except Exception as e:
        click.secho(">> %s" %e, fg='red')
        return

    click.secho('>> Delete device commplete!', fg='white')

# @cli.command()
# def test():
#     click.echo('<a href="http://www.google.com">Google</a>')
