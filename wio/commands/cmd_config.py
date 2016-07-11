import click
from wio.wio import pass_wio
from wio.wio import choise_server

@click.command()
@click.argument('command', metavar='<main-server>')
# @click.option('--mserver', default= None, help='Set main server ip, such as 192.168.21.48')
@pass_wio
def cli(wio, command):
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
        choise_server(wio)
