import click
from wio import termui
from wio import serial_list
from wio import udp
from wio.wio import pass_wio
from wio.wio import node_list_endpoint
from wio.wio import nodes_create_endpoint
from wio.wio import nodes_rename_endpoint
from wio.wio import boards
from wio.wio import WIO_LINK_V1_0
from wio.wio import WIO_NODE_V1_0
from wio.wio import verify

import requests
import re
import time
import serial
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


def get_new(mserver_url, token, board):
    '''get node sn and key'''
    thread = termui.waiting_echo("Getting message from Server...")
    thread.daemon = True
    thread.start()
    try:
        params = {"name":"node000", "board":board, "access_token":token}
        r = requests.post("%s%s" %(mserver_url, nodes_create_endpoint), params=params, timeout=10, verify=verify)
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
        return None
    except Exception as e:
        thread.stop('')
        thread.join()
        click.secho(">> %s" %e, fg='red')
        return None

    thread.stop('')
    thread.join()

    return json_response

def check_connect(mserver_url, token, node_sn, d_name):
    thread = termui.waiting_echo('')
    thread.daemon = True
    thread.start()
    state_online = False
    for i in range(60):
        thread.message("The Wio now attempt to connect to Server... [%s]" %(60-i))
        time.sleep(1)
        try:
            params = {"access_token":token}
            r = requests.get("%s%s" %(mserver_url, node_list_endpoint), params=params)
            r.raise_for_status()
            json_response = r.json()
        except Exception as e:
            continue

        for n in json_response["nodes"]:
            if n["node_sn"] == node_sn and n["online"]:
                click.echo(click.style('\r> ', fg='green') + "The Wio connect to Server success.              ")
                thread.message("Setting Wio name...")
                state_online = True
                break
        if state_online:
            break

    if not state_online:
        thread.stop('')
        thread.join()
        click.echo(click.style('\r>> ', fg='red') + "The Wio connect to Server failure.")
        click.secho("\n> Please check info you enter, Try again.", fg='white', bold=True)
        return None

    try:
        params = {"name":d_name,"node_sn":node_sn,"access_token":token}
        r = requests.post("%s%s" %(mserver_url, nodes_rename_endpoint), params=params)
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
        return None
    except Exception as e:
        thread.stop('')
        thread.join()
        click.secho(">> %s" %e, fg='red')
        return None
    click.echo(click.style('\r> ', fg='green') + "Set Wio name success.")

    thread.stop('')
    thread.join()
    click.echo()
    click.echo(click.style('> ', fg='green') +
        click.style("Configuration complete!", fg='white', bold=True))

    return True

def upd_send(msvr, msvr_ip, xsvr, xsvr_ip, node_sn, node_key):
    click.echo()
    click.secho('! ', fg='green', nl=False)
    click.echo("PROTIP: " +
        click.style("Wireless setup of Wio!", fg='white'))
    click.secho('! ', fg='green', nl=False)
    click.echo("PROTIP: " +
        click.style("You need ", fg='white') +
        click.style("manually ", fg='green') +
        click.style("change your Wi-Fi network to Wio's network.", fg='white'))
    click.secho('! ', fg='green', nl=False)
    click.echo("PROTIP: " +
        click.style("You will lose your connection to the internet periodically.", fg='white'))
    click.echo()

    click.prompt(click.style('? ', fg='green') +
        click.style('Please connect to the Wio_* network now. Press enter when ready', bold=True),
        default='', show_default=False)

    while 1:
        if not click.confirm(click.style('? ', fg='green') +
                    click.style("Would you like to manually enter your Wi-Fi network configuration?", bold=True),
                    default=False):
            thread = termui.waiting_echo("Asking the Wio to scan for nearby Wi-Fi networks...")
            thread.daemon = True
            thread.start()

            ssid_list = udp.udp_list()

            if ssid_list:
                thread.stop('')
                thread.join()
            else:
                thread.stop("\rsearch failure...\n")
                return None

            while 1:
                for x in range(len(ssid_list)):
                    click.echo("%s.) %s" %(x, ssid_list[x]))
                click.secho('? ', fg='green', nl=False)
                value = click.prompt(
                            click.style('Please select the network to which your Wio should connect', bold=True),
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

        click.echo(click.style('> ', fg='green') + "Here's what we're going to send to the Wio:")
        click.echo()
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
    # get version
    version = udp.udp_version()
    # send udp command
    send_flag = False
    if version <= 1.1:
        cmd = "APCFG: %s\t%s\t%s\t%s\t%s\t%s\t\r\n" %(ap, ap_pwd, node_key, node_sn, xsvr_ip, msvr_ip)
    elif version >=1.2:
        cmd = "APCFG: %s\t%s\t%s\t%s\t%s\t%s\t\r\n" %(ap, ap_pwd, node_key, node_sn, xsvr, msvr)
    else:
        cmd = "APCFG: %s\t%s\t%s\t%s\t%s\t%s\t\r\n" %(ap, ap_pwd, node_key, node_sn, xsvr, msvr)
    # click.echo(cmd)
    result = udp.send(cmd)
    thread.stop('')
    thread.join()

    if not result:
        return None
    else:
        return {'name':d_name}

def serial_send(msvr, msvr_ip, xsvr, xsvr_ip, node_sn, node_key, port):
    ### check is configure mode?
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
        return None

    thread.stop('')
    thread.join()

    if flag:
        click.secho('> ', fg='green', nl=False)
        click.secho("Found Wio.", fg='green', bold=True)
        click.echo()
    else:
        click.secho('> ', fg='green', nl=False)
        click.secho("No nearby Wio detected.", fg='white', bold=True)
        if click.confirm(click.style('? ', fg='green') +
                click.style("Would you like to wait and monitor for Wio entering configure mode", bold=True),
                default=True):

            thread = termui.waiting_echo("Waiting for a wild Wio to appear... (press ctrl + C to exit)")
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
            click.secho("Found Wio.", fg='green', bold=True)
            click.echo()
        else:
            click.secho('> ', fg='green', nl=False)
            click.secho("\nQuit wio setup!", bg='white', bold=True)

    while 1:
        if not click.confirm(click.style('? ', fg='green') +
                    click.style("Would you like to manually enter your Wi-Fi network configuration?", bold=True),
                    default=False):
            thread = termui.waiting_echo("Asking the Wio to scan for nearby Wi-Fi networks...")
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
                return None

            while 1:
                for x in range(len(ssid_list)):
                    click.echo("%s.) %s" %(x, ssid_list[x]))
                click.secho('? ', fg='green', nl=False)
                value = click.prompt(
                            click.style('Please select the network to which your Wio should connect', bold=True),
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

        click.echo(click.style('> ', fg='green') + "Here's what we're going to send to the Wio:")
        click.echo()
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
    ## get version
    version = 1.1
    with serial.Serial(port, 115200, timeout=10) as ser:
        cmd = 'VERSION\r\n'
        ser.write(cmd.encode('utf-8'))
        res = ser.readline()
        try:
            version = float(re.match(r"([0-9]+.[0-9]+)", res).group(0))
        except Exception as e:
            version = 1.1

    send_flag = False
    while 1:
        with serial.Serial(port, 115200, timeout=10) as ser:
            if version <= 1.1:
                cmd = "APCFG: %s\t%s\t%s\t%s\t%s\t%s\t\r\n" %(ap, ap_pwd, node_key, node_sn, xsvr_ip, msvr_ip)
            elif version >= 1.2:
                cmd = "APCFG: %s\t%s\t%s\t%s\t%s\t%s\t\r\n" %(ap, ap_pwd, node_key, node_sn, xsvr, msvr)
            else:
                cmd = "APCFG: %s\t%s\t%s\t%s\t%s\t%s\t\r\n" %(ap, ap_pwd, node_key, node_sn, xsvr, msvr)
            # click.echo(cmd)
            ser.write(cmd.encode('utf-8'))
            if "ok" in ser.readline():
                click.echo(click.style('\r> ', fg='green') + "Send Wi-Fi information to device success.")
                thread.stop('')
                thread.join()
                send_flag = True
        if send_flag:
            break

    if send_flag:
        return {'name': d_name}
    else:
        return None

@click.command()
@pass_wio
def cli(wio):
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
    mserver_url = wio.config.get("mserver", None)
    msvr_ip = wio.config.get("mserver_ip", None)
    if not mserver_url or not token:
        click.echo(click.style('>> ', fg='red') + "Please login, use " +
            click.style("wio login", fg='green'))
        return
    msvr = urlparse(mserver_url).hostname
    xsvr = msvr
    xsvr_ip = msvr_ip
    board = ''

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
        click.style("Server", fg='green'))
    click.echo()
    click.secho('? ', fg='green', nl=False)
    if not click.confirm(click.style('Would you like continue?', bold=True), default=True):
        click.echo('Quit setup!')
        return

    ### choice board
    while 1:
        for x in range(len(boards)):
            click.echo("%s.) %s" %(x, boards[x]))
        click.secho('? ', fg='green', nl=False)
        value = click.prompt(click.style('Please choice the board type', bold=True), type=int)
        if value >= 0 and value < len(boards):
            board = boards[value]
            break
        else:
            click.echo(click.style('>> ', fg='red') + "invalid input.")

    r = get_new(mserver_url, token, board)
    if not r:
        return
    node_key = r["node_key"]
    node_sn = r["node_sn"]

    ### list wio with serial
    if board == WIO_LINK_V1_0:
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
            click.secho('> ', fg='green', nl=False)
            click.echo("No devices detected via USB.")
            # click.echo('>> change your network to wio_?')
            click.secho('? ', fg='green', nl=False)
            value = click.confirm(
                click.style('Would you like to enter Wi-Fi setup mode?', bold=True), default=True)

            #### udp setup
            r = upd_send(msvr, msvr_ip, xsvr, xsvr_ip, node_sn, node_key)
            if not r:
                return
            d_name = r['name']
            check_connect(mserver_url, token, node_sn, d_name)
            return
            
        click.echo(click.style('> ', fg='green') + "I have detected a " +
            click.style("Wio ", fg='green') + "connected via USB.")

        r = serial_send(msvr, msvr_ip, xsvr, xsvr_ip, node_sn, node_key, port)
        if not r:
            return
        d_name = r['name']
        check_connect(mserver_url, token, node_sn, d_name)
    elif board == WIO_NODE_V1_0:
        r = upd_send(msvr, msvr_ip, xsvr, xsvr_ip, node_sn, node_key)
        if not r:
            return
        d_name = r['name']
        check_connect(mserver_url, token, node_sn, d_name)
