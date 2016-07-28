import click
from wio.wio import pass_wio
from wio import udp


@click.command()
# @click.option('--APCFG', nargs=2)
@click.option('--get-debug', is_flag=True, help="get debug status")
@click.option('--debug', type=click.Choice(['on', 'off']), help="enable/disable debug")
# @click.option('--VERSION', is_flag=True)
# @click.option('--Blank?', is_flag=True)
# @click.option('-p') #TODO(ten): support serial
@pass_wio
def cli(wio, get_debug, debug):
    '''
    Change setting of device.

    \b
    DOES:
        The config command lets you change setting of device through upd.
        1. Ensure your device is Configure Mode.
        2. Change your computer network to Wio's AP.

    \b
    EXAMPLE:
        wio config --debug [on|off], enable/disable wio debug
        wio config --get-debug, get wio debug status
    '''
    if debug:
        if debug == "on":
            cmd = "ENDEBUG: 1"
        elif debug == "off":
            cmd = "ENDEBUG: 0"
        if not cmd:
            return debug_error()
        result = udp.send(cmd)
        if not result:
            return debug_error()
        click.echo("Setting success!! Device will reboot!!")
    
    elif get_debug:
        try:
            result = udp.udp_debug()
        except Exception as e:
            return get_debug_error()
    
        if result == "1":
            click.echo("debug: on")
        elif result == '0':
            click.echo("debug: off")
        else:
            return get_debug_error()
            
    else:
        click.echo("Note:")
        click.echo("    1. Ensure your device is Configure Mode.")
        click.echo("    2. Change your computer network to Wio's AP.")
        click.echo()
        click.echo("Use:")
        click.echo("    wio config --debug [on|off], enable/disable wio debug")
        click.echo("    wio config --get-debug, get wio debug status")
        
def debug_error():
    click.echo("Setting failure!!")
    error_tip()

def get_debug_error():
    click.echo("Get debug status failure!!")
    error_tip()

def error_tip():
        click.echo("Note:")
        click.echo("    1. Ensure your device is Configure Mode.")
        click.echo("    2. Change your computer network to Wio's AP.")
