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
        wio config --debug on/off, enable/disable wio debug
        wio config --get-debug, get wio debug status
    '''
    if debug:
        if debug == "on":
            cmd = "ENDEBUG: 1"
        elif debug == "off":
            cmd = "ENDEBUG: 0"
        if not cmd:
            return click.echo("Setting failure!!")
        result = udp.send(cmd)
        if not result:
            return click.echo("Setting failure!!")
        click.echo("Setting success!!")
    
    elif get_debug:
        try:
            result = udp.udp_debug()
        except Exception as e:
            return click.echo("Get state failure!!")
    
        if result == "1":
            click.echo("debug: on")
        elif result == '0':
            click.echo("debug: off")
        else:
            click.echo("Get state failure!!")
            
    else:
        pass #TODO(ten) add tip
