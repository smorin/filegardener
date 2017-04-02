# -*- coding: utf-8 -*-
""" This is the runner module that collects config information and runs the
initial code
"""
from __future__ import print_function
import click
import logging
import sys
import os
import os.path
import sys
import getopt
import hashlib
import io

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

def eprint(*args, **kwargs):
    """ prints to stderr, using the 'from __future__ import print_function' """
    print(*args, file=sys.stderr, **kwargs)

__version__ = '1.6.9' 
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
        once = False
        for dirpath, dirnames, files in os.walk(mydir):
            LOGGER.debug(dirpath)
            once = True
            innercount = innercount + 1
        if once:
            innercount = innercount - 1 # decrement by one so it excludes counting itself
    return innercount

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('file', nargs=-1, required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True))
@click.option('--basedir', '-b', default=False, help='base directory to join each file path to', required=False, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--exitonfail/--no-exitonfail', '-e', default=False, help='turn on/off exit on first failure')
@click.pass_obj
def rmfiles(ctx, file, basedir, exitonfail):
    """
    rmfiles will delete a set of files listed in the input file(s)
    """    
    if not (type(file) == list or type(file) == tuple):
        raise Exception("Wrong input type should be a list: %s" % type(file))
    
    result = True
    reason = None
    failed_once = False
    
    for file_name in file:
        with io.open(file_name, "r", encoding="utf8") as f:
            for line in f:
                file_path = line.rstrip()
                if basedir:
                    file_path = os.path.abspath(os.path.join(basedir, file_path))
                try:
                    result, reason = rmfile(file_path)
                except OSError as excep:
                    result = False
                    reason = str(excep)
                if not result:
                    click.echo("%s\t%s" % (file_path, reason))
                    failed_once = True
                    if exitonfail:
                        sys.exit(1)

    if failed_once:
        sys.exit(1)

def rmfile(file_path):
    result = False
    reason = None
    if validate_test_file(file_path):
        os.remove(file_path) # tmp don't remove files till tested
        result = True
    else:
        result = False
        reason = "wasn't a file"
    return result, reason
    

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('file', nargs=-1, required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True))
@click.option('--basedir', '-b', default=False, help='base directory to join each file path to', required=False, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--exitonfail/--no-exitonfail', '-e', default=False, help='turn on/off exit on first failure')
@click.pass_obj
def rmdirs(ctx, file, basedir, exitonfail):
    """
    rmdirs will delete a set of dirs listed in the input file(s)
    """
    if not (type(file) == list or type(file) == tuple):
        raise Exception("Wrong input type should be a list: %s" % type(file))
    
    result = True
    reason = None
    failed_once = False
    
    
    for file_name in file:
        with io.open(file_name, "r", encoding="utf8") as f:
            all_dirs = f.readlines()
            all_dirs = sorted(all_dirs, key=len, reverse=True) # so long child dirs get removed first
            for line in all_dirs:
                file_path = line.rstrip()
                if basedir:
                    file_path = os.path.abspath(os.path.join(basedir, file_path))
                try:
                    result, reason = rmdir(file_path)
                except OSError as excep:
                    result = False
                    reason = str(excep)
                if not result:
                    click.echo("%s\t%s" % (file_path, reason))
                    failed_once = True
                    if exitonfail:
                        sys.exit(1)
    if failed_once:
        sys.exit(1)

def rmdir(dir_path):
    result = False
    reason = None
    if validate_test_dir(dir_path):
        os.rmdir(dir_path) # tmp don't remove files till tested
        result = True
    else:
        reason = "wasn't a directory"
    return result, reason

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('destdir', nargs=1, required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--basedir', '-b', default=False, help='base directory to join each file path to', required=False, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--targetdir', '-b', default=False, help='location to move all files from', required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--file', '-f', default=False, help='file for input files', required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True))
@click.pass_obj
def mvbase(ctx, destdir, basedir, file):
    """
    mvbase will move a set of files from their locations, at target directory to destdir
    """
    click.echo("TODO: not implemented yet")
    sys.exit(1)
    failed = False

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('file', nargs=-1, required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True))
@click.option('--basedir', '-b', default=False, help='base directory to join each file path to', required=False, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--exitonfail/--no-exitonfail', '-e', default=False, help='turn on/off exit on first failure')
@click.pass_obj
def validatefiles(ctx, file, basedir, exitonfail):
    """
    validatefiles reads in a file of file paths and checks that it exists
    """
    Result, Count = validate_files(file, basedir, exitonfail)
    if not Result:
        sys.exit(1)
    else:
        sys.exit(0)

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('file', nargs=-1, required=True, type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True))
@click.option('--basedir', '-b', default=False, help='base directory to join each file path to', required=False, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--exitonfail/--no-exitonfail', '-e', default=False, help='turn on/off exit on first failure')
@click.pass_obj
def validatedirs(ctx, file, basedir, exitonfail):
    """
    validatedirs reads in a file of dir paths and checks that it exists and passes test
    """
    Result, Count = validate_dirs(file, basedir, exitonfail)
    if not Result:
        sys.exit(1)
    else:
        sys.exit(0)

def validate_files(file, basedir, exitonfail):
    return validate_paths(file, basedir, exitonfail, validate_test_file)

def validate_dirs(file, basedir, exitonfail):
    return validate_paths(file, basedir, exitonfail, validate_test_dir)

def validate_paths(file_paths, basedir, exitonfail, path_tester):
    failed = False
    count = 0
    if not type(file_paths) == list:
        raise Exception("Wrong input type should be a list")

    for failed_path in validatepath_yield(file_paths, basedir, path_tester):
        failed = True
        count = count + 1
        click.echo(failed_path)
        if failed and exitonfail:
            return False, count
    if failed:
        return False, count
    else:
        return True, count

def validatepath_yield(files, basedir, path_tester):
    for file_name in files:
        with io.open(file_name, "r", encoding="utf8") as f:
            for line in f:
                file_path = line.rstrip()
                if basedir:
                    file_path = os.path.abspath(os.path.join(basedir, file_path))
                if not path_tester(file_path):
                    yield file_path

def validate_test_file(file_path):
    if os.path.isfile(file_path):
        return True
    else:
        return False

def validate_test_dir(dir_path):
    if os.path.isdir(dir_path):
        return True
    else:
        return False

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument('checkdir', nargs=-1, required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--relpath/--no-relpath', '-r', default=False, help='turn on/off relative path - default off')
@click.pass_obj
def emptydirs(ctx, checkdir, relpath):
    """
    emptydir command lists all the directories that no file in it or it's sub directories
    """
    if relpath:
        basepath = os.getcwd()
        for i in emptydirs_yield(checkdir):
            click.echo(os.path.relpath(i, basepath))
    else:
        for i in emptydirs_yield(checkdir):
            click.echo(i)

def get_parent_dir(mydir):
	return os.path.abspath(os.path.join(mydir,os.path.pardir))

def emptydirs_yield(checkdir):
    """
    emptydirs command prints list of directories in one or more checkdirs
    """
    # http://stackoverflow.com/questions/19699127/efficient-array-concatenation
    for mydir in checkdir:
        is_leaf = False
        is_empty = False
        parent_dict = {}
        my_parent = None
        abs_dirpath = None
        for dirpath, dirnames, files in os.walk(mydir, topdown=False):
            # if ctx['debug']: # debug needs to be defined
            #     LOGGER.debug("%s %s %s" % (dirpath, dirnames, files))

            if len(dirnames) == 0:
                is_leaf = True
            else:
                is_leaf = False

            if len(files) == 0:
                if is_leaf:
                    is_empty = True
                else:
                    is_empty = parent_dict[os.path.abspath(dirpath)][0]
            else:
                is_empty = False

            my_parent = get_parent_dir(dirpath)

            if my_parent in parent_dict:
                entry = parent_dict[my_parent]
                parent_dict[my_parent] = [is_empty and entry[0], entry[1] + 1]
            else:
                parent_dict[my_parent] = [is_empty,  1]
            
            if is_leaf:
                if is_empty:
                    yield dirpath
            else:
                abs_dirpath = os.path.abspath(dirpath)
                if abs_dirpath in parent_dict:
                    entry = parent_dict[abs_dirpath]
                    del parent_dict[abs_dirpath] # because your traversing the dirs with topdown=False it should have already seen all children
                    if len(dirnames) != entry[1]:
                        raise Exception("Entries don't match the number of dirs, so a subdir wasn't checked.")
                    else:
                        if entry[0] and is_empty:
                            yield abs_dirpath

@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option('--srcdir', '-s', multiple=True, required=True, help='directories to check',  type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.argument('checkdir', nargs=-1, required=True, type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True))
@click.option('--relpath/--no-relpath', '-r', default=False, help='turn on/off relative path - default off')
@click.pass_obj
def dedup(ctx, srcdir, checkdir, relpath):
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
@click.option('--relpath/--no-relpath', '-r', default=False, help='turn on/off relative path - default off')
@click.option('--failonerror/--no-failonerror', '-f', default=True, help='turn on/off failing on error - default on')
@click.pass_obj
def onlycopy(ctx, srcdir, checkdir, relpath, failonerror):
    """
    onlycopy command prints list of all the files that aren't in the srcdir
    """
    if relpath:
        basepath = os.getcwd()
        for i in onlycopy_yield(srcdir, checkdir, failonerror):
            click.echo(os.path.relpath(i, basepath))
    else:
        for i in onlycopy_yield(srcdir, checkdir, failonerror):
            click.echo(i)
    
def onlycopy_yield(srcdir, checkdir, failonerror=True):
    """
    onlycopy command prints list of all the files that aren't in the srcdir
    """
    check_dir_no_overlap(srcdir, checkdir)

    # http://stackoverflow.com/questions/19699127/efficient-array-concatenation

    basefiles = []
    for mydir in srcdir:
        innerdir = get_files_and_size_from_dir(mydir)
        basefiles.extend(innerdir)

    size_dict = create_size_dict(basefiles)

    for comparedir in checkdir:
        only_files = get_only_copy(size_dict, comparedir, failonerror)

        LOGGER.debug("Length %s" % len(only_files))
        for thefile in only_files:
            yield thefile

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
    files = [ (os.path.abspath(os.path.join(dirpath,filename)),os.path.getsize(os.path.join(dirpath,filename))) for dirpath, dirnames, files in os.walk(topdir) for filename in files if not os.path.islink(os.path.join(dirpath,filename))]
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
    if_match_return_true=True means find duplicates
    if_match_return_true=False means find if there is only one copy of it.
    """
        
    files = []
    
    if_match_return_true = True

    files = [ os.path.abspath(os.path.join(dirpath,filename)) # return absolute path of file that matches criteria
                for dirpath, dirnames, files in os.walk(topdir) 
                    for filename in files 
                        if os.path.getsize(os.path.join(dirpath,filename)) in size_dict 
                        and is_match(os.path.getsize(os.path.join(dirpath,filename)), # size
                        os.path.abspath(os.path.join(dirpath,filename)), # file
                        size_dict[os.path.getsize(os.path.join(dirpath,filename))], # file_list
                        if_match_return_true) # if_match_return_value
            ] 
    return files  

def get_only_copy(size_dict, topdir, failonerror=True):
    """
    if_match_return_true=True means find duplicates
    if_match_return_true=False means find if there is only one copy of it.
    """
    
    files = []
    
    if_match_return_true = False
    
    # The logic is for all the directories and for each file in each directory
    # test the following if is_not_symlink and (not in size or is_not_match )
    files = [ os.path.abspath(os.path.join(dirpath,filename)) # return absolute path of file that matches criteria
                for dirpath, dirnames, files in os.walk(topdir) 
                    for filename in files 
                        if not os.path.islink(os.path.join(dirpath,filename)) and (os.path.getsize(os.path.join(dirpath,filename)) not in size_dict 
                        or is_match(os.path.getsize(os.path.join(dirpath,filename)), # size
                        os.path.abspath(os.path.join(dirpath,filename)), # file
                        size_dict[os.path.getsize(os.path.join(dirpath,filename))], # file_list
                        if_match_return_true, # if_match_return_value
                        failonerror)) ] # failonerror
    return files 
  

def is_match(size, file, file_list, if_match_return_value, is_error_fatal=True):
    """
    if_match_return_value=True means find duplicates
    if_match_return_value=False means find not duplicates
    is_error_fatal=True
    
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
        try:
            return compare_whole_file(size, file, file_list, if_match_return_value, is_error_fatal)
        except IOError as myioerror:
            if is_error_fatal:
                raise myioerror
            else:
                eprint()
            
    else:
        for file_to_compare in file_list:
            try:
                if compare_first_4k(file, file_to_compare):
                    # TODO: Optimize by saving the md5 for each check if a list
                    if compare_md5(file, file_to_compare):
                        return if_match_return_value
            except IOError as myioerror:
                if is_error_fatal:
                    raise myioerror
                else:
                    eprint("{}:{}".format(file, file_to_compare))
        return not if_match_return_value

def compare_whole_file(size, file, file_list, if_match_return_value, is_error_fatal):
    file_bytes = b''
    file_to_compare_bytes = b''
    try:
        with open(file,"rb") as f:
            file_bytes = f.read(size)
            if len(file_bytes) != size:
                raise Exception("Did not read the expected file size")
    except IOError as myioerror:
        if is_error_fatal:
            raise myioerror
        else:
            eprint("{}".format(file))
    
    for file_to_compare in file_list:
        try:
            with open(file_to_compare,"rb") as f:
                file_to_compare_bytes = f.read(size)
                if len(file_to_compare_bytes) != size:
                    raise IOError("Filegardener - compare_whole_file: Did not read the expected file size:{}".format(size))
        except IOError as myioerror:
            if is_error_fatal:
                raise myioerror
            else:
                eprint("{}:{}".format(file, file_to_compare))
        if file_bytes == file_to_compare_bytes:
            return if_match_return_value
    return not if_match_return_value

def compare_first_4k(file, file_to_compare):
    '''
        Should compare the first 4k of each file to see if they match
    '''
    file_bytes = b''
    file_to_compare_bytes = b''
    with open(file,"rb") as f:
        file_bytes = f.read(4096)
        if len(file_bytes) != 4096:
            raise IOError("Filegardener - compare_first_4k: Did not read the expected file size:{}".format(4096))
    with open(file_to_compare,"rb") as f:
        file_to_compare_bytes = f.read(4096)
        if len(file_bytes) != 4096:
            raise IOError("Filegardener - compare_first_4k: Did not read the expected file size:{}".format(4096))
    if file_bytes == file_to_compare_bytes:
        return True
    else:
        return False

def compare_md5(file, file_to_compare):
    '''
        compares the md5 to see if there is a match

        Block size directly depends on the block size of your filesystem
        to avoid performances issues
        Here I have blocks of 4096 octets (Default NTFS)
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
        return True
    else:
        return False
        
        
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

