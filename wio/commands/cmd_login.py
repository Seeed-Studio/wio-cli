import click
from wio.wio import pass_wio

@click.command()
@pass_wio
def cli(wio):
    '''
    Login with your Wio account.

    \b
    DOES:
        Login and save an access token for interacting with your account on the Wio.

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
