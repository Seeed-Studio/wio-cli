import click
from wio.wio import pass_wio
from wio import udp


@click.command()
@click.option('--send', nargs=1, type=unicode, help="Sends a UDP command to the wio device")
@pass_wio
def cli(wio, send):
    '''
    Sends a UDP command to the wio device.

    \b
    DOES:
        Support "VERSION", "SCAN", "Blank?", "DEBUG", "ENDEBUG: 1", "ENDEBUG: 0"
        "APCFG: AP\\tPWDs\\tTOKENs\\tSNs\\tSERVER_Domains\\tXSERVER_Domain\\t\\r\\n",
        Note:
        1. Ensure your device is Configure Mode.
        2. Change your computer network to Wio's AP.

    \b
    EXAMPLE:
        wio udp --send [command], send UPD command
    '''
    command = send
    click.echo("UDP command: {}".format(command))
    result = udp.common_send(command)
    if result is None:
        return debug_error()
    else:
        click.echo(result)

def debug_error():
    click.echo("UDP command work failure!!")
    error_tip()
    
def error_tip():
        click.echo("Note:")
        click.echo("    1. Ensure your device is Configure Mode.")
        click.echo("    2. Change your computer network to Wio's AP.")
