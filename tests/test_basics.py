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

    def test_countfiles_one(self):
        """ test countfiles for a set of one files"""
        # filegardener.configure_logger(True,None)
        assert filegardener.count_files([],[os.path.abspath(os.path.join(os.getcwd(),'./test_data/emptydirs'))]) == 1

    def test_countfiles_zero(self):
        """ test countfiles for a set of zero files"""
        # filegardener.configure_logger(True,None)
        assert filegardener.count_files([],[os.path.abspath(os.path.join(os.getcwd(),'./test_data/emptydirs/main'))]) == 0

    def test_countfiles_twenty(self):
        """ test countfiles for a set of 20 files """
        # filegardener.configure_logger(True,None)
        assert filegardener.count_files([],[os.path.abspath(os.path.join(os.getcwd(),'./test_data/1dup/firstdir'))]) == 20

    def test_countdirs_sixteen(self):
        """ test countfiles for a set of zero files"""
        # filegardener.configure_logger(True,None)
        assert filegardener.count_dirs([],[os.path.abspath(os.path.join(os.getcwd(),'./test_data/emptydirs'))]) == 18

    def test_countdirs_three(self):
        """ test countfiles for a set of 20 files """
        # filegardener.configure_logger(True,None)
        assert filegardener.count_dirs([],[os.path.abspath(os.path.join(os.getcwd(),'./test_data/1dup/firstdir'))]) == 4

    def test_duplicate_one(self):
        """ test that there is only one duplicate"""

    @pytest.mark.parametrize('testdir',['3dupsof6', '1dup', 'identicaldirs'])
    def test_dedup(self, testdir):
        dup_tester(testdir)

    @pytest.mark.parametrize('testdir',['3dupsof6', '1dup', 'identicaldirs'])
    def test_dedup_reverse(self, testdir):
        dup_tester(testdir, reverse=True)

    @pytest.mark.parametrize('testdir',['emptydirs', 'nodups'])
    def test_dedup_none(self, testdir):
        dup_tester(testdir, noresults=True)

    @pytest.mark.parametrize('testdir',['1dup', 'nodups'])
    def test_only(self, testdir):
        only_tester(testdir)
    
    @pytest.mark.parametrize('testdir',['3dupsof6', '1dup', 'nodups'])
    def test_only_reverse(self, testdir):
        only_tester(testdir, reverse=True)
    
    @pytest.mark.parametrize('testdir',['emptydirs'])
    def test_only_none(self, testdir):
        only_tester(testdir, noresults=True)

    @pytest.mark.parametrize('testdir',['emptydirs', 'identicaldirs'])
    def test_only_none(self, testdir):
        only_tester(testdir, noresults=True, reverse=True)

    @pytest.mark.parametrize('testdir',['emptydirs', '7notemptydirs', '1dup'])
    def test_emptydirs(self, testdir):
        emptydirs_tester(testdir)
        
    @pytest.mark.parametrize('testdir',['identicaldirs', 'nodups'])
    def test_emptydirs_none(self, testdir):
        emptydirs_tester(testdir, noresults=True)

    def test_validatedirs(self):
        myinputfile = ['test_data/emptydirs/emptydirs_correct_results.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_dirs(file=myinputfile, basedir=mybasedir, exitonfail=True)
        assert result == True and count == 0

    def test_validatedirs_badbase(self):
        myinputfile = ['test_data/emptydirs/emptydirs_correct_results.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd(),'nonexistent'))
        result, count = filegardener.validate_dirs(file=myinputfile, basedir=mybasedir, exitonfail=False)
        assert count == 18 and result == False

    def test_validatedirs_badbase_firstfail(self):
        myinputfile = ['test_data/emptydirs/emptydirs_correct_results.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd(),'nonexistent'))
        result, count = filegardener.validate_dirs(file=myinputfile, basedir=mybasedir, exitonfail=True)
        assert count == 1 and result == False
        
    def test_validatedirs_badinputfile(self):
        myinputfile = ['test_data/empytdirs/nonexistent.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd(),'nonexistent'))
        with pytest.raises(IOError):
            result, count = filegardener.validate_dirs(file=myinputfile, basedir=mybasedir, exitonfail=True)

    def test_validatedirs_3baddirs_all(self):
        myinputfile = ['test_data/7notemptydirs/validatedirs_baddirs.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_dirs(file=myinputfile, basedir=mybasedir, exitonfail=False)
        assert result == False and count == 3

    def test_validatedirs_3baddirs_first(self):
        myinputfile = ['test_data/7notemptydirs/validatedirs_baddirs.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_dirs(file=myinputfile, basedir=mybasedir, exitonfail=True)
        assert result == False and count == 1

    def test_validatedirs_includesfile_first(self):
        myinputfile = ['test_data/7notemptydirs/validatedirs_includesfile.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_dirs(file=myinputfile, basedir=mybasedir, exitonfail=True)
        assert result == False and count == 1

    def test_validatedirs_includesfile_all(self):
        myinputfile = ['test_data/7notemptydirs/validatedirs_includesfile.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_dirs(file=myinputfile, basedir=mybasedir, exitonfail=False)
        assert result == False and count == 1
        
    def test_validatedirs_badfileargument(self):
        myinputfile = 'test_data/7notemptydirs/validatedirs_includesfile.txt'
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        with pytest.raises(Exception):
            result, count = filegardener.validate_dirs(file=myinputfile, basedir=mybasedir, exitonfail=False)


    def test_dirtest(self):
        """ this sanity test checks that if a directory path that doesn't exist when joined with a file path that points to a dir that doesn't exist"""
        mybasedir = os.path.abspath(os.path.join(os.getcwd(),'nonexistent'))
        file_path = 'test_data/7notemptydirs/main/subdir1'
        file_path = os.path.abspath(os.path.join(mybasedir, file_path))
        assert False == filegardener.validate_test_dir(file_path)

    def test_dirtest_path(self):
        """ this tests the file path joining does what we expects and joins paths with out magically correcting them"""
        mybasedir = os.path.abspath(os.path.join(os.getcwd(),'nonexistent'))
        file_path = 'test_data/7notemptydirs/main/subdir1'
        file_path_join = os.path.abspath(os.path.join(mybasedir, file_path))
        assert os.path.abspath(os.getcwd())+'/nonexistent/'+file_path == file_path_join


    def test_validatefiles(self):
        myinputfile = ['test_data/identicaldirs/correct_results.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_files(file=myinputfile, basedir=mybasedir, exitonfail=True)
        assert result == True and count == 0

    def test_validatefiles_badbase(self):
        myinputfile = ['test_data/identicaldirs/correct_results.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd(),'nonexistent'))
        result, count = filegardener.validate_files(file=myinputfile, basedir=mybasedir, exitonfail=False)
        assert count == 20 and result == False

    def test_validatefiles_badbase_firstfail(self):
        myinputfile = ['test_data/identicaldirs/correct_results.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd(),'nonexistent'))
        result, count = filegardener.validate_files(file=myinputfile, basedir=mybasedir, exitonfail=True)
        assert count == 1 and result == False
        
    def test_validatefiles_badinputfile(self):
        myinputfile = ['test_data/empytdirs/nonexistent.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd(),'nonexistent'))
        with pytest.raises(IOError):
            result, count = filegardener.validate_files(file=myinputfile, basedir=mybasedir, exitonfail=True)

    def test_validatefiles_3dirs_all(self):
        myinputfile = ['test_data/identicaldirs/validatefiles_includes_3dirs.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_files(file=myinputfile, basedir=mybasedir, exitonfail=False)
        assert result == False and count == 3

    def test_validatefiles_3dirs_first(self):
        myinputfile = ['test_data/identicaldirs/validatefiles_includes_3dirs.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_files(file=myinputfile, basedir=mybasedir, exitonfail=True)
        assert result == False and count == 1

    def test_validatefiles_includes_badfile_first(self):
        myinputfile = ['test_data/identicaldirs/validatefiles_includes_3nonexistent_files.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_files(file=myinputfile, basedir=mybasedir, exitonfail=True)
        assert result == False and count == 1

    def test_validatefiles_includes_badfile_all(self):
        myinputfile = ['test_data/identicaldirs/validatefiles_includes_3nonexistent_files.txt']
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        result, count = filegardener.validate_files(file=myinputfile, basedir=mybasedir, exitonfail=False)
        assert result == False and count == 3
        
    def test_validatefiles_badfileargument(self):
        myinputfile = 'test_data/7notemptydirs/validatedirs_includesfile.txt'
        mybasedir = os.path.abspath(os.path.join(os.getcwd()))
        with pytest.raises(Exception):
            result, count = filegardener.validate_files(file=myinputfile, basedir=mybasedir, exitonfail=False)


    @pytest.mark.parametrize(
        'other, result', (
            ("some string", True),
            ("another string", True)
        )
    )
    def test_paramertrize_example(self, other, result):
        """ Example of using parameters to make multiple call """
        assert (other == other) is result

def dup_tester(test_dir, reverse=False, noresults=False):
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
    
    if noresults:
        with pytest.raises(StopIteration):
            next(generator)
    else:
        with open(test_validation_file) as f:
            i = 0
            result_lookup = {}
            for line in f:
                file_name = line.rstrip('\n') # remove new lines from each line
                file_name = os.path.abspath(os.path.join(os.getcwd(), file_name))
                result_lookup[file_name] = file_name
            for line in generator:
                assert result_lookup[line] == line

def only_tester(test_dir, reverse=False, noresults=False):
    """ you give this method a path name and it looks uner test_data/ for that directory to test.  
    This test assumes that the order the duplicates will be found will be the same"""
    test_basedir = os.path.abspath(os.path.join(os.getcwd(),'test_data',test_dir))
    validation_file_name = ''
    dir1 = os.path.join(test_basedir,'firstdir')
    dir2 = os.path.join(test_basedir,'seconddir')
    if reverse: 
        validation_file_name = 'onlycopy_correct_results_reverse_input_dirs.txt'
        srcdir = [dir2]
        checkdir = [dir1]
    else:
        validation_file_name = 'onlycopy_correct_results.txt'
        srcdir = [dir1]
        checkdir = [dir2]
        
    test_validation_file = os.path.join(test_basedir,validation_file_name)
    generator = filegardener.onlycopy_yield(srcdir,checkdir)
    
    if noresults:
        with pytest.raises(StopIteration):
            next(generator)
    else:
        with open(test_validation_file) as f:
            i = 0
            result_lookup = {}
            for line in f:
                file_name = line.rstrip('\n') # remove new lines from each line
                file_name = os.path.abspath(os.path.join(os.getcwd(), file_name))
                result_lookup[file_name] = file_name
            for line in generator:
                assert result_lookup[line] == line

def emptydirs_tester(test_dir, noresults=False):
    """ you give this method a path name and it looks uner test_data/ for that directory to test.  
    This test assumes that the order the duplicates will be found will be the same"""
    test_basedir = os.path.abspath(os.path.join(os.getcwd(),'test_data',test_dir))

    validation_file_name = 'emptydirs_correct_results.txt'
        
    test_validation_file = os.path.join(test_basedir,validation_file_name)
    generator = filegardener.emptydirs_yield([test_basedir])
    
    if noresults:
        with pytest.raises(StopIteration):
            next(generator)
    else:
        with open(test_validation_file) as f:
            i = 0
            result_lookup = {}
            for line in f:
                file_name = line.rstrip('\n') # remove new lines from each line
                file_name = os.path.abspath(os.path.join(os.getcwd(), file_name))
                result_lookup[file_name] = file_name
            for line in generator:
                assert result_lookup[line] == line

