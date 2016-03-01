import click
from wio import termui
from wio.wio import pass_wio
from wio.wio import nodes_delete_endpoint
from wio.wio import verify

import requests

@click.command()
@click.argument('sn')
@pass_wio
def cli(wio, sn):
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
