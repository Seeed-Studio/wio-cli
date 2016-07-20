import click
import sys
import requests
import time
import hashlib
from wio import termui
from wio import config
from wio.wio import pass_wio
from wio.wio import login_endpoint
from wio.wio import ext_user_endpoint
from wio.wio import verify
from wio.wio import choise_server


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
        click.echo(click.style('> ', fg='green') + "Current server is: " +
            click.style(mserver, fg='green'))
        if click.confirm(click.style('Would you like login with a different server?', bold=True), default=False):
            choise_server(wio)
    else:
        choise_server(wio)
        
    email = click.prompt(click.style('? ', fg='green') +
        click.style('Please enter your email address', bold=True), type=str)
    password = click.prompt(click.style('? ', fg='green') +
        click.style('Please enter your password', bold=True), hide_input=True, type=str)

    thread = termui.waiting_echo("Sending login details...")
    thread.daemon = True
    thread.start()
            
    try:
        if wio.config.get("server") == 'Customize':
            server_url = wio.config.get("mserver")
            json_response = login_wio(server_url, email, password)
            token = json_response['token']
        else:
            res = login_seeed(email, password)
            token = res['data']['token']
            user_id = res['data']['userid']
            ext_user(wio.config.get("mserver"), email, user_id, token)
    except Exception as e:
        thread.stop('')
        thread.join()
        click.secho(">> %s" %e, fg='red')
        return

    wio.set_config('email', email)
    wio.set_config('token', token)

    thread.stop('')
    thread.join()
    click.secho("\r> ", fg='green', nl=False)
    click.echo("Successfully completed login!")

def get_sign(url, time):
    APPID = config.SEEED_APPID
    APPKEY = config.SEEED_APPKEY
    COMMON = config.SEEED_COMMON
    li = [APPID, APPKEY, COMMON, url, str(time)]
    li.sort()
    sign = ''
    for l in li:
        sign += l
    h = hashlib.sha1(sign.encode('utf-8'))
    return h.hexdigest()
    
def login_seeed(email, passwd):
    url = "http://bazaar.seeed.cc/api/index.php?r=common/user/login"
    timestamp = int(time.time())
    payload = dict(
        email=email,
        password=passwd,
        source='4',
        api_key='wiolink',
        timestamp = timestamp,
        sign = get_sign('r=common/user/login', timestamp))
    r = requests.post(url, data=payload)
    res = r.json()
    if res.get('errorcode') != 0:
        raise Exception('error', res.get('msgs'))
    return res
    
def ext_user(server_url, email, user_id, token):
    payload = dict(
        email=email,
        bind_id=user_id,
        token=token,
        bind_region=config.WIO_REGION,
        secret=config.WIO_SECKET
        )
    r = requests.post("%s%s" %(server_url, ext_user_endpoint), data=payload,
        timeout=10, verify=verify)
    res = r.json()
    if r.status_code != 200:
        raise Exception('error', res.get('error'))
    return res
    
def login_wio(server_url, email, passwd):
    payload = dict(email=email, password=passwd)
    r = requests.post("%s%s" %(server_url, login_endpoint), data=payload,
        timeout=10, verify=verify)
    res = r.json()
    if r.status_code != 200:
        raise Exception('error', res.get('error'))
    return res
