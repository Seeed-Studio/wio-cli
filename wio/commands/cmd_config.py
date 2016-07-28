import click
from wio.wio import pass_wio
from wio import udp


@click.command()
# @click.option('--APCFG', nargs=2)
@click.option('--DEBUG', is_flag=True, help="12")
@click.option('--ENDEBUG', type=click.Choice(['on', 'off']), help="12")
# @click.option('--VERSION', is_flag=True)
# @click.option('--Blank?', is_flag=True)
# @click.option('-p') #TODO(ten): support serial
@pass_wio
def cli(wio, debug, endebug):
    '''
    Change setting of device.

    \b
    DOES:
        The config command lets you change setting of device through upd.
        1. Ensure your device is Configure Mode.
        2. Change your computer network to Wio's AP.

    \b
    EXAMPLE:
        wio config --ENDEBUG on/off, enable/disable wio debug
        wio config --DEBUG, check wio debug state
    '''
    # print apcfg, debug, version
    # print endebug, debug
    if endebug:
        cmd = ''
        if endebug == "on":
            cmd = "ENDEBUG: 1"
        elif endebug == "off":
            cmd = "ENDEBUG: 0"
        else:
            return click.echo("Use param on or off")
        # print cmd
        if not cmd:
            return click.echo("Setting failure!!")
        result = udp.send(cmd)
        if not result:
            return click.echo("Setting failure!!")
        click.echo("Setting success!!")
        
    if debug:
        try:
            result = udp.udp_debug()
            # print 1, result
        except Exception as e:
            return click.echo("Get state failure!!")
        
        if result == "1":
            click.echo("DEBUG: on")
        elif result == '0':
            click.echo("DEBUG: off")
        else:
            click.echo("Get state failure!!")
        
        
        
        
