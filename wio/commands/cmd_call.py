import click
from wio import termui
from wio.wio import pass_wio
from wio.wio import verify

import requests

@click.command()
@click.argument('token')
@click.argument('method')
@click.argument('endpoint')
# @click.option('--xchange', help='xchange server url')
@pass_wio
def cli(wio, method, endpoint, token,):
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
