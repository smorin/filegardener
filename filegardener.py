""" This is the runner module that collects config information and runs the
initial code
"""
import click
import logging

# Setup Logging

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        """ This is a dummy NullHandler implementation in-case NullHandler class not found"""
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

LOGGER = logging.getLogger(__name__)

__version__ = '1.0.1' 
__author__ = 'Steve Morin'

# Done setting up logging

def print_version(ctx, param, value):
    """ Prints the version of this software"""
    # pylint: disable=unused-argument
    if not value:
        return
    click.echo('Version '+__version__)
    ctx.exit()

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help', '-?'])

# This makes it so when there is no subcommand --help isn't automatically called
@click.group(invoke_without_command=False, context_settings=CONTEXT_SETTINGS)
@click.option('--debug/--no-debug', '-d', default=False, envvar='BS_DEBUG',
              help='turn on/off debug mode')
@click.option('--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True,
              help='print programs version')
@click.pass_context
def cli(ctx, debug):
    """ Parent cli call"""
    ctx.obj = dict(debug=debug)
    if ctx.invoked_subcommand is None:
        raise Exception("Runtime Error")
        # This should never happen because invoke_without_command=False, to allow this to be called set invoke_without_command=True
    else:
        pass


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--srcdir', '-s', multiple=True, required=True, help='directories to check',  type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.argument('checkdir', nargs=-1, required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.pass_obj
def dedup(ctx, srcdir, checkdir):
    click.echo('basedir %s to check folder %s' % (srcdir, checkdir))
    for x in srcdir:
        click.echo('srcdir: %s!' % x)
    for x in checkdir:
        click.echo('srcdir: %s!' % x)
        click.echo(click.format_filename(x))

# This allows the function "def cli" above to be easily called because of click library
if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    cli()


