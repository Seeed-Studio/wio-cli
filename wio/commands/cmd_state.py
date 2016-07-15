import click
from wio.wio import pass_wio

@click.command()
@pass_wio
def cli(wio):
    '''
    Login state.

    \b
    DOES:
        Display login email, token, server url.

    \b
    USE:
        wio state
    '''
    user_token = wio.config.get("token", None)
    mserver_url = wio.config.get("mserver", None)
    if not mserver_url or not user_token:
        click.echo(click.style('>> ', fg='red') + "Please login, use " +
            click.style("wio login", fg='green'))
        return

    email = wio.config.get("email",None)
    server = wio.config.get("server",None)
    token = wio.config.get("token",None)
    click.secho('> ', fg='green', nl=False)
    click.echo("server: " + click.style(server, fg='green', bold=True) + ', ' +
        click.style(mserver_url, fg='green', bold=True))
    click.secho('> ', fg='green', nl=False)
    click.echo("email:  " + click.style(email, fg='green', bold=True))
    click.secho('> ', fg='green', nl=False)
    click.echo("token:  " + click.style(token, fg='green', bold=True))
