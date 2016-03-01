import click
from wio import termui
from wio.wio import pass_wio
from wio.wio import node_list_endpoint
from wio.wio import node_resources_endpoint
from wio.wio import well_known_endpoint
from wio.wio import nodes_delete_endpoint
from wio.wio import boards
from wio.wio import verify

import requests

@click.command()
@pass_wio
def cli(wio):
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
