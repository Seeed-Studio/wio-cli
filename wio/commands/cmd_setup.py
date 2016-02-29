import click
from wio.wio import pass_wio

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
    api_prefix = wio.config.get("mserver", None)
    if not api_prefix or not token:
        click.echo(click.style('>> ', fg='red') + "Please login, use " +
            click.style("wio login", fg='green'))
        return

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
        click.style("main server", fg='green'))
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

    thread = termui.waiting_echo("Getting message from main server...")
    thread.daemon = True
    thread.start()
    try:
        params = {"name":"node000", "board":board, "access_token":token}
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
            return
        click.echo(click.style('> ', fg='green') +
            "I have detected a " +
            click.style("Wio ", fg='green') +
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
                    return

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

            msvr = wio.config.get("mserver", None)
            click.echo(click.style('> ', fg='green') + "Here's what we're going to send to the Wio:")
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
                    thread.message("The Wio now attempt to connect to main server...")
                    send_flag = True
            if send_flag:
                break

        # token = wio.config.get("token", None)
        # api_prefix = wio.config.get("mserver", None)
        # if not api_prefix or not token:
        #     click.echo("Please login [wio login]")
        #     return

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
                    click.echo(click.style('\r> ', fg='green') + "The Wio connect to main server success.              ")
                    thread.message("Setting Wio name...")
                    state_online = True
                    break
            if state_online:
                break

            thread.message("The Wio now attempt to connect to main server... [%s]" %(30-i))
            time.sleep(1)

        if not state_online:
            thread.stop('')
            thread.join()
            click.echo(click.style('\r>> ', fg='red') + "The Wio connect to main server failure.")
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
        click.echo(click.style('\r> ', fg='green') + "Set Wio name success.")

        thread.stop('')
        thread.join()
        click.echo()
        click.echo(click.style('> ', fg='green') +
            click.style("Configuration complete!", fg='white', bold=True))
    elif board == WIO_NODE_V1_0:
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
                    return

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

            msvr = wio.config.get("mserver", None)
            click.echo(click.style('> ', fg='green') + "Here's what we're going to send to the Wio:")
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
        cmd = "APCFG: %s\t%s\t%s\t%s\t%s\t%s\t\r\n" %(ap, ap_pwd, node_key, node_sn, msvr_ip, xsvr_ip)
        result = udp.send(cmd)

        # token = wio.config.get("token", None)
        # api_prefix = wio.config.get("mserver", None)
        # if not api_prefix or not token:
        #     click.echo("Please login [wio login]")
        #     return
        # click.echo(json_response)

        state_online = False
        for i in range(60):
            thread.message("The Wio now attempt to connect to main server... [%s]" %(30-i))
            time.sleep(1)
            try:
                params = {"access_token":token}
                r = requests.get("%s%s" %(api_prefix, node_list_endpoint), params=params)
                r.raise_for_status()
                json_response = r.json()
            except Exception as e:
                continue

            for n in json_response["nodes"]:
                if n["node_sn"] == node_sn and n["online"]:
                    click.echo(click.style('\r> ', fg='green') + "The Wio connect to main server success.              ")
                    thread.message("Setting Wio name...")
                    state_online = True
                    break
            if state_online:
                break

        if not state_online:
            thread.stop('')
            thread.join()
            click.echo(click.style('\r>> ', fg='red') + "The Wio connect to main server failure.")
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
        click.echo(click.style('\r> ', fg='green') + "Set Wio name success.")

        thread.stop('')
        thread.join()
        click.echo()
        click.echo(click.style('> ', fg='green') +
            click.style("Configuration complete!", fg='white', bold=True))
