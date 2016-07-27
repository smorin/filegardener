# -*- coding: utf-8 -*-
""" This is the runner module that collects config information and runs the
initial code
"""
import click
import logging
import sys
import os
import os.path
import sys
import getopt
import hashlib

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

__version__ = '1.1.1' 
__author__ = 'Steve Morin'
__script_name__ = 'filegardener'

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
    """ For help on individual commands type:

\b
        filegardener <command> --help
    """
    ctx.obj = dict(debug=debug)
    verbosity = None # currently not set or used
    configure_logger(debug,verbosity)

    if ctx.invoked_subcommand is None:
        raise Exception("Runtime Error")
        # This should never happen because invoke_without_command=False, to allow this to be called set invoke_without_command=True
    else:
        pass

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('checkdir', nargs=-1, required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.pass_obj
def countfiles(ctx, checkdir):
    """
    countfiles command counts the number of files in the directories you give it
    """

    return_value = count_files(ctx, checkdir)

    click.echo(return_value)

def count_files(ctx, checkdir):
    innercount = 0
    LOGGER.debug("checkdir: %s" % checkdir)
    if type(checkdir) == str:
        raise Exception("Wrong input type should be a list")
    for mydir in checkdir:
        for dirpath, dirnames, files in os.walk(mydir):
            for filename in files:
                LOGGER.debug("filename: %s" % filename)
                innercount = innercount + 1
    return innercount

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('checkdir', nargs=-1, required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.pass_obj
def countdirs(ctx, checkdir):
    """
    countdirs command counts the number of directories in the directories you give it (excludes dirs you give it)
    """
    return_value = count_dirs(ctx, checkdir)

    click.echo(return_value)
    
def count_dirs(ctx, checkdir):
    """ count_dirs does the actual counting of the directories """
    innercount = 0
    if type(checkdir) == str:
        raise Exception("Wrong input type should be a list")
    for mydir in checkdir:
        innercount = innercount - 1 # decrement by one so it excludes counting itself
        for dirpath, dirnames, files in os.walk(mydir):
            LOGGER.debug(dirpath)
            innercount = innercount + 1
    return innercount

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('checkdir', nargs=-1, required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.pass_obj
def emptydirs(ctx, checkdir):
    """
    emptydir command lists all the directories that no file in it or it's sub directories
    """

    innercount = 0
    for mydir in checkdir:
        innercount = innercount - 1 # decrement by one so it excludes counting itself
        for dirpath, dirnames, files in os.walk(mydir, topdown=False):
            if ctx['debug']:
                LOGGER.debug("%s %s %s" % (dirpath, dirnames, files))
                # click.echo(dirpath)
            innercount = innercount + 1
    click.echo(innercount)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--srcdir', '-s', multiple=True, required=True, help='directories to check',  type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.argument('checkdir', nargs=-1, required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--relpath/--no-relpath', '-r', default=False, help='turn on/off relative path - default off')
@click.pass_obj
def dedup(ctx, srcdir, checkdir,relpath):
    """
    Dedup command prints list of duplicate files in one or more checkdirs
    """
    if relpath:
        basepath = os.getcwd()
        for i in dedup_yield(srcdir, checkdir):
            click.echo(os.path.relpath(i, basepath))
    else:
        for i in dedup_yield(srcdir, checkdir):
            click.echo(i)
    
def dedup_yield(srcdir, checkdir):
    """
    Dedup command prints list of duplicate files in one or more checkdirs
    """
    check_dir_no_overlap(srcdir, checkdir)

    # http://stackoverflow.com/questions/19699127/efficient-array-concatenation

    basefiles = []
    for mydir in srcdir:
        innerdir = get_files_and_size_from_dir(mydir)
        basefiles.extend(innerdir)

    size_dict = create_size_dict(basefiles)

    for comparedir in checkdir:
        dup_files = get_duplicate_files(size_dict, comparedir)

        LOGGER.debug("Length %s" % len(dup_files))
        for thefile in dup_files:
            yield thefile



@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--srcdir', '-s', multiple=True, required=True, help='directories to check',  type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.argument('checkdir', nargs=-1, required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.pass_obj
def tryyield(ctx, srcdir, checkdir):
    """ test yield """
    for i in try_yield():
        click.echo("item: %s" % i)

def try_yield():
    for i in range(10):
        yield i



def check_dir_no_overlap(srcdir, checkdir):
    for x in checkdir:
        for y in srcdir:
            if x == y:
                click.echo("source and checkdir are the same, they must be different")
                sys.exit(1)
            elif x.startswith(y) or y.startswith(x):
                click.echo("source and checkdir are a subdirectory of one or the other source(%s), checkdir(%s)" % (x, y) )
                sys.exit(1)    

def get_files_and_size_from_dir(topdir):
    """ Finds all the files under a specific directory. Returns a list of the absolute path for
    all of these files."""
    if not os.path.isdir(topdir):
        raise Exception("You submitted a director that isn't one'")
    files = [ (os.path.abspath(os.path.join(dirpath,filename)),os.path.getsize(os.path.join(dirpath,filename))) for dirpath, dirnames, files in os.walk(topdir) for filename in files ]
    return files
    
def create_size_dict(files_size):
    size_dict = {}
    for file, size in files_size:
        if size in size_dict:
            size_dict[size].append(file)
        else:
            size_dict[size] = [file]
    return size_dict

# Example usage of os.walk
# topdir = '.'
# all_paths = [ (dirpath, dirnames, files) for dirpath, dirnames, files in os.walk(topdir) ]
#
# for item in all_paths:
#     print(item)
# ('./test_dedup/1dup/seconddir/tests', ['testserver'], ['__init__.py', 'compat.py', 'conftest.py', 'test_hooks.py', 'test_lowlevel.py', 'test_requests.py', 'test_structures.py', 'test_testserver.py', 'test_utils.py', 'utils.py'])
# ('./test_dedup/1dup/seconddir/tests/testserver', [], ['__init__.py', 'server.py'])
# ('./test_dedup/identialdirs', ['firstdir', 'seconddir'], [])

def get_duplicate_files(size_dict, topdir):
    """
    findonlycopy=False means find duplicates
    findonlycopy=True means find if there is only one copy of it.
    """
        
    files = []
    
    if_match_return_true = True

    files = [ os.path.abspath(os.path.join(dirpath,filename)) # return absolute path of file that matches criteria
                for dirpath, dirnames, files in os.walk(topdir) 
                    for filename in files 
                        if os.path.getsize(os.path.join(dirpath,filename)) in size_dict 
                        and is_match(os.path.getsize(os.path.join(dirpath,filename)), #size
                        os.path.abspath(os.path.join(dirpath,filename)), # file
                        size_dict[os.path.getsize(os.path.join(dirpath,filename))], #file_list
                        if_match_return_true) #if_match_return_value
            ] 
    return files  

def get_only_copy(size_dict, topdir):
    """
    findonlycopy=False means find duplicates
    findonlycopy=True means find if there is only one copy of it.
    """
    
    files = []

    files = [ os.path.abspath(os.path.join(dirpath,filename)) for dirpath, dirnames, files in os.walk(topdir) for filename in files if os.path.getsize(os.path.join(dirpath,filename)) not in size_dict or is_match(os.path.getsize(os.path.join(dirpath,filename)),os.path.abspath(os.path.join(dirpath,filename)),size_dict[os.path.getsize(os.path.join(dirpath,filename))],findonlycopy) ]
    return files 
  

def is_match(size, file, file_list, if_match_return_value):
    """
    if_match_return_value=True means find duplicates
    if_match_return_value=False means find not duplicates
    
    Algorithm:
    files being compared are the same size
    
    if file is less than 4096 bytes
        just compare if bytes of source file and file_list are the same
    if file is 4096 bytes or greater
        for the source file and each file in the checklist
            compare first 4k of source file and check file
            if match check md5 of each file
    
    """
    if size < 4096:
        return compare_whole_file(size, file, file_list, if_match_return_value)
    else:
        for file_to_compare in file_list:
            if compare_first_4k(file, file_to_compare, if_match_return_value):
                # TODO: Optimize by saving the md5 for each check if a list
                if compare_md5(file, file_to_compare, if_match_return_value):
                    return if_match_return_value
        return not if_match_return_value

def compare_whole_file(size, file, file_list, if_match_return_value):
    file_bytes = b''
    file_to_compare_bytes = b''
    with open(file,"rb") as f:
        file_bytes = f.read(size)
        if len(file_bytes) != size:
            raise Exception("Did not read the expected file size")
    for file_to_compare in file_list:
        with open(file_to_compare,"rb") as f:
            file_to_compare_bytes = f.read(size)
            if len(file_to_compare_bytes) != size:
                raise Exception("Did not read the expected file size")
        if file_bytes == file_to_compare_bytes:
            return if_match_return_value
    return not if_match_return_value

def compare_first_4k(file, file_to_compare, if_match_return_value):
    '''
        if_match_return_value=True means find duplicates
        if_match_return_value=False means find not duplicates
    '''
    file_bytes = b''
    file_to_compare_bytes = b''
    with open(file,"rb") as f:
        file_bytes = f.read(4096)
        if len(file_bytes) != 4096:
            raise Exception("Did not read the expected file size")
    with open(file_to_compare,"rb") as f:
        file_to_compare_bytes = f.read(4096)
        if len(file_bytes) != 4096:
            raise Exception("Did not read the expected file size")
    if file_bytes == file_to_compare_bytes:
        return if_match_return_value
    else:
        return not if_match_return_value

def compare_md5(file, file_to_compare, if_match_return_value):
    '''
        Block size directly depends on the block size of your filesystem
        to avoid performances issues
        Here I have blocks of 4096 octets (Default NTFS)
    
        if_match_return_value=True means find duplicates
        if_match_return_value=False means find not duplicates
        '''
    # TODO I have to check that block size thing
    md5_base = None
    md5_to_compare = None

    # find out blocksize
    # echo “hello” > blocksize.txt
    # du -h blocksize.txt

    block_size=256*128*2 # 256*128*2=65536
    md5 = hashlib.md5()
    with open(file,'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            md5.update(chunk)
        md5_base = md5.hexdigest()

    block_size=256*128*2 # 256*128*2=32768
    md5 = hashlib.md5()
    with open(file_to_compare,'rb') as f:
        for chunk in iter(lambda: f.read(block_size), b''):
            md5.update(chunk)
        md5_to_compare = md5.hexdigest()
    
    if md5_base == md5_to_compare:
        return if_match_return_value
    else:
        return not if_match_return_value
        
        
def configure_logger(debug_on, verbosity):
    """ Configure the top level logger with sensible defaults that can be configured
    with a configuration file
    """
    # TODO: make logger accept configuration for config location and log destination
    if debug_on or verbosity:
        log_level = logging.WARN

        if verbosity == 1:
            log_level = logging.INFO
        elif verbosity == 2:
            log_level = logging.DEBUG

        if debug_on:
            log_level = logging.DEBUG

        toplevel_logger = logging.getLogger(__script_name__)
        toplevel_logger.setLevel(log_level)

        # create console handler and set level to debug
        strhdlr = logging.FileHandler('%s.log' % __script_name__)
        strhdlr.setLevel(log_level)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to strhdlr
        strhdlr.setFormatter(formatter)

        # add strhdlr to logger
        toplevel_logger.addHandler(strhdlr)

# This allows the function "def cli" above to be easily called because of click library
if __name__ == '__main__':
    # pylint: disable=no-value-for-parameter
    cli()

