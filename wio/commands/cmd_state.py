import click
from wio.wio import pass_wio

@click.command()
@pass_wio
def cli(wio):
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
