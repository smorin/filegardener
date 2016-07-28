# coding: utf-8
""" This module is the first test module"""
import pytest
import filegardener
import os
import os.path
import io


# Reference: http://pythontesting.net/framework/pytest/pytest-session-scoped-fixtures/
# Reference: http://pythontesting.net/framework/pytest/pytest-fixtures/

class TestBasics(object):
    """
    This class could have been called anything and can have second class here
    """

    @pytest.fixture(autouse=True, scope='session')
    def setup(self):
        """
        Here is where things get setup
        """
        with io.open("test_data/DIRECTORIES.txt", "r", encoding="utf8") as fp:
            for line in fp:
                dirpath = line.rstrip('\n')
                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)
                


    possible_keys = pytest.mark.parametrize('key', ('accept', 'ACCEPT', 'aCcEpT', 'Accept'))

    @possible_keys
    def test_example_passinginputs(self, key):
        """ Example unit test passing invalues with a decorator """
        assert key == key

    def test_importclick(self):
        """ testing that importing a core package works """
        import click

    def test_example(self):
        """ Example of a simple unit test """
        assert "string" == "string"

    def test_sanity_check(self):
        """ Checking that filegardener runner can be called """
        assert filegardener.__version__ != None

    def test_author(self):
        """ test that author variable can be called """
        assert filegardener.__author__ == 'Steve Morin'

    def test_cwd_is_relative(self):
        """ test the cwd that tests run in is relative to test_data """
        assert os.path.abspath(os.path.join('.','test_data')) == os.path.abspath(os.path.join(os.getcwd(),'test_data'))

    def test_dir_test_data_exists(self):
        """ test that test_data dir is found and a directory"""
        assert os.path.isdir(os.path.abspath(os.path.join(os.getcwd(),'test_data'))) == True

    def test_dir_exists_emptydirs(self):
        """ test that the subdirectory emptydirs in test data exists"""
        assert os.path.isdir(os.path.abspath(os.path.join(os.getcwd(),'./test_data/emptydirs'))) == True

    def test_countfiles_zero(self):
        """ test countfiles for a set of zero files"""
        # filegardener.configure_logger(True,None)
        assert filegardener.count_files([],[os.path.abspath(os.path.join(os.getcwd(),'./test_data/emptydirs'))]) == 0

    def test_countfiles_twenty(self):
        """ test countfiles for a set of 20 files """
        # filegardener.configure_logger(True,None)
        assert filegardener.count_files([],[os.path.abspath(os.path.join(os.getcwd(),'./test_data/1dup/firstdir'))]) == 20

    def test_countdirs_sixteen(self):
        """ test countfiles for a set of zero files"""
        # filegardener.configure_logger(True,None)
        assert filegardener.count_dirs([],[os.path.abspath(os.path.join(os.getcwd(),'./test_data/emptydirs'))]) == 16

    def test_countdirs_three(self):
        """ test countfiles for a set of 20 files """
        # filegardener.configure_logger(True,None)
        assert filegardener.count_dirs([],[os.path.abspath(os.path.join(os.getcwd(),'./test_data/1dup/firstdir'))]) == 3

    def test_duplicate_one(self):
        """ test that there is only one duplicate"""

    @pytest.mark.parametrize('testdir',['3dupsof6', '1dup', 'identicaldirs'])
    def test_dedup(self, testdir):
        dup_tester(testdir)

    @pytest.mark.parametrize('testdir',['3dupsof6', '1dup', 'identicaldirs'])
    def test_dedup_reverse(self, testdir):
        dup_tester(testdir, reverse=True)

    @pytest.mark.parametrize(
        'other, result', (
            ("some string", True),
            ("another string", True)
        )
    )
    def test_paramertrize_example(self, other, result):
        """ Example of using parameters to make multiple call """
        assert (other == other) is result

def dup_tester(test_dir, reverse=False, none=False):
    """ you give this method a path name and it looks uner test_data/ for that directory to test.  
    This test assumes that the order the duplicates will be found will be the same"""
    test_basedir = os.path.abspath(os.path.join(os.getcwd(),'test_data',test_dir))
    validation_file_name = ''
    dir1 = os.path.join(test_basedir,'firstdir')
    dir2 = os.path.join(test_basedir,'seconddir')
    if reverse: 
        validation_file_name = 'correct_results_reverse_input_dirs.txt'
        srcdir = [dir2]
        checkdir = [dir1]
    else:
        validation_file_name = 'correct_results.txt'
        srcdir = [dir1]
        checkdir = [dir2]
        
    test_validation_file = os.path.join(test_basedir,validation_file_name)
    generator = filegardener.dedup_yield(srcdir,checkdir)
    with open(test_validation_file) as f:
        i = 0
        for line in f:
            file_name = line.rstrip('\n') # remove new lines from each line
            assert os.path.abspath(os.path.join(os.getcwd(),file_name)) == next(generator)

