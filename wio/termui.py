import sys
from time import sleep
import click
import threading

class waiting_echo(threading.Thread):
    def __init__(self, msg):
        threading.Thread.__init__(self)
        self.msg = msg
        self.exiting=False
        self.flag = True
    def run(self):
        while not self.exiting:
            if self.flag:
                click.echo( "\r*%-80s" %self.msg, nl=False)
                click.echo("\b"*(80-len(self.msg)), nl=False)
                self.flag = False
            else:
                click.echo( "\rO%-80s" %self.msg, nl=False)
                click.echo("\b"*(80-len(self.msg)), nl=False)
                self.flag = True
            sys.stdout.flush()
            sleep(0.1)
        click.echo( "\r%-80s" %self.msg, nl=False)
        click.echo('\r', nl=False)
        # click.echo("\b"*(80-len(self.msg)))
    def message(self, msg):
        self.msg = msg
    def stop(self, msg):
        self.exiting = True
        self.msg = msg
