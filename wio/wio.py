import os
import sys
import posixpath
import json

import click
import requests

# url_prefix = "http://192.168.21.48:8080"
url_prefix = "https://iot.seeed.cc"
login_endpoint = "/v1/user/login"
node_list_endpoint = "/v1/nodes/list"


class Wio(object):

    def __init__(self):
        # self.home = home
        self.config = {}
        self.verbose = False

    def set_config(self, key, value):
        self.config[key] = value
        # cur_dir = os.path.split(os.path.realpath(__file__))[0]
        cur_dir = os.path.abspath(os.path.expanduser("~/.wio"))
        db_file_path = '%s/config.json' % cur_dir
        open("%s/config.json"%cur_dir,"w").write(json.dumps(self.config))
        if self.verbose:
            click.echo('config[%s] = %s' % (key, value), file=sys.stderr)

    def __repr__(self):
        return '<Wio %r>' % self.home


pass_wio = click.make_pass_decorator(Wio, ensure=True)


@click.group()
# @click.option('--wio-home', envvar='REPO_HOME', default='.wio',
#               metavar='PATH', help='Changes the wiository folder location.')
# @click.option('--config', nargs=2, multiple=True,
#               metavar='KEY VALUE', help='Overrides a config key/value pair.')
@click.option('--verbose', '-v', is_flag=True,
              help='Enables verbose mode.')
@click.version_option('0.0.3')
@click.pass_context
def cli(ctx, verbose):
    """Wio is a command line tool that showcases how to build complex
    command line interfaces with Click.

    This tool is supposed to look like a distributed version control
    system to show how something like this can be structured.
    """
    # Create a wio object and remember it as as the context object.  From
    # this point onwards other commands can refer to it by using the
    # @pass_wio decorator.
    ctx.obj = Wio()
    ctx.obj.verbose = verbose
    # config.json
    # cur_dir = os.path.split(os.path.realpath(__file__))[0]
    cur_dir = os.path.abspath(os.path.expanduser("~/.wio"))
    if not os.path.exists(cur_dir):
        text = {"email":"", "token":""}
        os.mkdir(cur_dir)
        open("%s/config.json"%cur_dir,"w").write(json.dumps(text))
    db_file_path = '%s/config.json' % cur_dir
    config = json.load(open(db_file_path))
    ctx.obj.config = config

@cli.command()
@click.option('--email', prompt='email', help='The developer\'s email address')
@click.option('--password', prompt='password', hide_input=True, help='The login password.')
@pass_wio
def login(wio, email, password):
    '''login with your wio link account'''
    # click.echo(email)
    # click.echo(password)
    params = {"email":email, "password":password}
    r = requests.post("%s%s" %(url_prefix, login_endpoint), params=params)
    token = r.json().get("token", None)
    wio.set_config('email', email)
    wio.set_config('token', token)
    if token:
        click.echo("login success!")
    else:
        click.echo(r.json().get("error", None))


@cli.command()
@pass_wio
def list(wio):
    '''List wio links'''
    token = wio.config["token"]
    params = {"access_token":token}
    r = requests.get("%s%s" %(url_prefix, node_list_endpoint), params=params)
    json = r.json()
    # print json
    click.echo("%10s %6s %s" %("name", "on/off", "node_key"))
    for n in json["nodes"]:
        click.echo("%10s %6s %s" %(n["name"], n["online"], n["node_key"]))

@cli.command()
@pass_wio
def state(wio):
    '''login state'''
    email = wio.config["email"]
    token = wio.config["token"]
    click.echo("email: %s" %email)
    click.echo("token: %s" %token)

# @cli.command()
# @click.argument('src')
# @click.argument('dest', required=False)
# @click.option('--shallow/--deep', default=False,
#               help='Makes a checkout shallow or deep.  Deep by default.')
# @click.option('--rev', '-r', default='HEAD',
#               help='Clone a specific revision instead of HEAD.')
# @pass_wio
# def clone(wio, src, dest, shallow, rev):
#     """Clones a wiository.
#
#     This will clone the wiository at SRC into the folder DEST.  If DEST
#     is not provided this will automatically use the last path component
#     of SRC and create that folder.
#     """
#     if dest is None:
#         dest = posixpath.split(src)[-1] or '.'
#     click.echo('Cloning wio %s to %s' % (src, os.path.abspath(dest)))
#     wio.home = dest
#     if shallow:
#         click.echo('Making shallow checkout')
#     click.echo('Checking out revision %s' % rev)
#
#
# @cli.command()
# @click.confirmation_option()
# @pass_wio
# def delete(wio):
#     """Deletes a wiository.
#
#     This will throw away the current wiository.
#     """
#     click.echo('Destroying wio %s' % wio.home)
#     click.echo('Deleted!')
#
#
# @cli.command()
# @click.option('--username', prompt=True,
#               help='The developer\'s shown username.')
# @click.option('--email', prompt='E-Mail',
#               help='The developer\'s email address')
# @click.password_option(help='The login password.')
# @pass_wio
# def setuser(wio, username, email, password):
#     """Sets the user credentials.
#
#     This will override the current user config.
#     """
#     wio.set_config('username', username)
#     wio.set_config('email', email)
#     wio.set_config('password', '*' * len(password))
#     click.echo('Changed credentials.')
#
#
# @cli.command()
# @click.option('--message', '-m', multiple=True,
#               help='The commit message.  If provided multiple times each '
#               'argument gets converted into a new line.')
# @click.argument('files', nargs=-1, type=click.Path())
# @pass_wio
# def commit(wio, files, message):
#     """Commits outstanding changes.
#
#     Commit changes to the given files into the wiository.  You will need to
#     "wio push" to push up your changes to other wiositories.
#
#     If a list of files is omitted, all changes wiorted by "wio status"
#     will be committed.
#     """
#     if not message:
#         marker = '# Files to be committed:'
#         hint = ['', '', marker, '#']
#         for file in files:
#             hint.append('#   U %s' % file)
#         message = click.edit('\n'.join(hint))
#         if message is None:
#             click.echo('Aborted!')
#             return
#         msg = message.split(marker)[0].rstrip()
#         if not msg:
#             click.echo('Aborted! Empty commit message')
#             return
#     else:
#         msg = '\n'.join(message)
#     click.echo('Files to be committed: %s' % (files,))
#     click.echo('Commit message:\n' + msg)
#
#
# @cli.command(short_help='Copies files.')
# @click.option('--force', is_flag=True,
#               help='forcibly copy over an existing managed file')
# @click.argument('src', nargs=-1, type=click.Path())
# @click.argument('dst', type=click.Path())
# @pass_wio
# def copy(wio, src, dst, force):
#     """Copies one or multiple files to a new location.  This copies all
#     files from SRC to DST.
#     """
#     for fn in src:
#         click.echo('Copy from %s -> %s' % (fn, dst))
