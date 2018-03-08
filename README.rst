filegardener
============
File gardener - file maintenance utilities - file dedup, only copy detection, prune empty dirs


.. image:: https://img.shields.io/pypi/v/filegardener.svg
   :target: https://pypi.python.org/pypi/filegardener

.. image:: https://img.shields.io/travis/smorin/filegardener/master.svg
   :target: http://travis-ci.org/smorin/filegardener

.. image:: https://readthedocs.org/projects/filegardener/badge/?version=latest
   :target: http://filegardener.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/filegardener.svg?maxAge=2592000   

* `Github Page <https://github.com/smorin/filegardener>`_
* `Issue Tracking <https://github.com/smorin/filegardener/issues>`_


Contributions
-------------

I am completely open to contributions, just open a issue if you want to suggest a feature so we can discuss.  If you want a project I need help implementing `mvbase`. I don't accept pull requests with out unit tests, you can look at examples


Install
-------
::

	> pip install filegardener

If you don't have pip it's also easy to install https://pip.pypa.io/en/stable/installing/

When filegardener installs it's installed on the commandline for you so you can just do.

::

	> filegardener --help


Build
-----
::

	> make

Use-Cases
---------

Checking for duplicate files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you want to get a list of all files that are duplicates in a second directory.

::


Checking for the last or only copy of a file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes you want to check for the last or only copy of a file lives on a second drive or directory.  This way you can make sure you don't delete the last copy of a file.

A common example would be if you have a bunch of USB Pen Drives and you want to wipe the drives clean but don't want to delete the last copy of a file.  You can use this to compare all the files on your computer with what's on your pen drive.

Example:
::

	time filegardener onlycopy --srcdir ~/Pictures --srcdir ~/Music  /Volumes/MyUSBDrive/ | tee list_onlycopyfiles_in_dst_dir.txt

If you want not fail on error and capture the list of file you only have 1 copy of and list of error in trying to check any file.  This command will save the list of file you only have one copy of in stdout.log and any errors in stderr.log
::

	time filegardener onlycopy --no-failonerror --srcdir ~/Pictures --srcdir ~/Music /Volumes/MyUSBDrive > >(tee stdout.log) 2> >(tee stderr.log >&2)


Todo's
-------------
* click plugin integration
* filegardener histogram -file size
* filegardener check per bucket
* filegardener optimize is_match
*

Usage Summary
-------------

::

	Usage: filegardener [OPTIONS] COMMAND [ARGS]...

	  For help on individual commands type:

	          filegardener <command> --help
      

	Options:
	  -d, --debug / --no-debug  turn on/off debug mode
	  --version                 print programs version
	  -?, -h, --help            Show this message and exit.

	Commands:
	  countdirs      countdirs command counts the number of...
	  countfiles     countfiles command counts the number of files...
	  dedup          Dedup command prints list of duplicate files...
	  emptydirs      emptydir command lists all the directories...
	  mvbase         mvbase will move a set of files from their...
	  onlycopy       onlycopy command prints list of all the files...
	  rmdirs         rmdirs will delete a set of dirs listed in...
	  rmfiles        rmfiles will delete a set of files listed in...
	  validatedirs   validatedirs reads in a file of dir paths and...
	  validatefiles  validatefiles reads in a file of file paths...

countdirs
---------
::

	> filegardener countdirs --help

::

	Usage: filegardener countdirs [OPTIONS] CHECKDIR...

	  countdirs command counts the number of directories in the directories you
	  give it (excludes dirs you give it)

	Options:
	  -?, -h, --help  Show this message and exit.

countfiles
----------
::

	> filegardener countfiles --help

::

	Usage: filegardener countfiles [OPTIONS] CHECKDIR...

	  countfiles command counts the number of files in the directories you give
	  it

	Options:
	  -?, -h, --help  Show this message and exit.

dedup
-----
::

	> filegardener dedup --help

::

	Usage: filegardener dedup [OPTIONS] CHECKDIR...

	  Dedup command prints list of duplicate files in one or more checkdirs

	Options:
	  -s, --srcdir DIRECTORY        directories to check  [required]
	  -r, --relpath / --no-relpath  turn on/off relative path - default off
	  -?, -h, --help                Show this message and exit.
	  
emptydirs
---------
::

	> filegardener emptydirs --help

::

	Usage: filegardener emptydirs [OPTIONS] CHECKDIR...

	  emptydir command lists all the directories that no file in it or it's sub
	  directories

	Options:
	  -r, --relpath / --no-relpath  turn on/off relative path - default off
	  -?, -h, --help                Show this message and exit.
	  
mvbase
------

This function isn't implemented yet and is a TODO:, if you want to contribute a pull request with tests that would be great!

::

	> filegardener mvbase --help

::

	Usage: filegardener mvbase [OPTIONS] DESTDIR

	  mvbase will move a set of files from their locations, at target directory
	  to destdir

	Options:
	  -b, --basedir DIRECTORY    base directory to join each file path to
	  -b, --targetdir DIRECTORY  location to move all files from  [required]
	  -f, --file PATH            file for input files  [required]
	  -?, -h, --help             Show this message and exit.

onlycopy
--------
::

	> filegardener onlycopy --help

::

	Usage: filegardener onlycopy [OPTIONS] CHECKDIR...

	  onlycopy command prints list of all the files that aren't in the srcdir

	Options:
	  -s, --srcdir DIRECTORY          directories to check  [required]
	  -r, --relpath / --no-relpath    turn on/off relative path - default off
	  -f, --failonerror / --no-failonerror
	                                  turn on/off failing on error - default on
	  -?, -h, --help                  Show this message and exit.

rmdirs
------
::

	> filegardener rmdirs --help
	
::

	Usage: filegardener rmdirs [OPTIONS] FILE...

	  rmdirs will delete a set of dirs listed in the input file(s)

	Options:
	  -b, --basedir DIRECTORY         base directory to join each file path to
	  -e, --exitonfail / --no-exitonfail
	                                  turn on/off exit on first failure
	  -?, -h, --help                  Show this message and exit.

rmfiles
-------
::

	> filegardener rmfiles --help

::

	Usage: filegardener rmfiles [OPTIONS] FILE...

	  rmfiles will delete a set of files listed in the input file(s)

	Options:
	  -b, --basedir DIRECTORY         base directory to join each file path to
	  -e, --exitonfail / --no-exitonfail
	                                  turn on/off exit on first failure
	  -?, -h, --help                  Show this message and exit.

validatedirs
------------
::

	> filegardener validatedirs --help

::

	Usage: filegardener validatedirs [OPTIONS] FILE...

	  validatedirs reads in a file of dir paths and checks that it exists and
	  passes test

	Options:
	  -b, --basedir DIRECTORY         base directory to join each file path to
	  -e, --exitonfail / --no-exitonfail
	                                  turn on/off exit on first failure
	  -?, -h, --help                  Show this message and exit.

validatefiles
-------------
::

	> filegardener validatefiles --help

::

	Usage: filegardener validatefiles [OPTIONS] FILE...

	  validatefiles reads in a file of file paths and checks that it exists

	Options:
	  -b, --basedir DIRECTORY         base directory to join each file path to
	  -e, --exitonfail / --no-exitonfail
	                                  turn on/off exit on first failure
	  -?, -h, --help                  Show this message and exit.
