# coding: utf-8
""" This module is the first test module"""
import pytest
import filegardener
import os
import os.path
import io
import shutil
from click.testing import CliRunner

import pdb

def debug():
    import pdb; pdb.set_trace()


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
                dirpath = line.rstrip()
                if not os.path.exists(dirpath):
                    os.makedirs(dirpath)
        src = 'test_data/onlycopysymfirst/firstdir/brokensymlink' # symlink file that is created
        dst = 'test_data/onlycopysymfirst/firstdir/doesnotexist' # symlink points to this
        
        if not os.path.lexists(src): # lexists will return true even for broken symlinks
            os.symlink(dst, src)
        
        src = 'test_data/onlycopysymsecond/seconddir/brokensymlink' # symlink file that is created
        dst = 'test_data/onlycopysymsecond/seconddir/doesnotexist' # symlink points to this
        if not os.path.lexists(src): # lexists will return true even for broken symlinks
            os.symlink(dst, src)


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

    def test_versions_equal(self):
        """ Example of a simple unit test """
        version = ''
        with open('VERSION') as file:
            version = file.readline()
            version = version.rstrip()
        assert version == filegardener.__version__

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
        onlycopy_tester(testdir)
    
    @pytest.mark.parametrize('testdir',['3dupsof6', '1dup', 'nodups'])
    def test_only_reverse(self, testdir):
        onlycopy_tester(testdir, reverse=True)
    
    @pytest.mark.parametrize('testdir',['emptydirs'])
    def test_only_none(self, testdir):
        onlycopy_tester(testdir, noresults=True)

    @pytest.mark.parametrize('testdir',['emptydirs', 'identicaldirs'])
    def test_only_none(self, testdir):
        onlycopy_tester(testdir, noresults=True, reverse=True)

    @pytest.mark.parametrize('testdir',['onlycopy', 'onlycopysymfirst', 'onlycopysymsecond'])
    def test_only_none(self, testdir):
        onlycopy_tester(testdir, noresults=False, reverse=False)

    @pytest.mark.parametrize('testdir',['emptydirs', '7notemptydirs', '1dup'])
    def test_emptydirs(self, testdir):
        emptydirs_tester(testdir)
        
    @pytest.mark.parametrize('testdir',['identicaldirs', 'nodups'])
    def test_emptydirs_none(self, testdir):
        emptydirs_tester(testdir, noresults=True)

    def test_onlycopy_regex_filter_everything(self):
        """ test onlycopy regex so that is filters out all results even when it would have some with out the regex """
        # filegardener onlycopy --srcdir=test_data/onlycopy/firstdir/ test_data/onlycopy/seconddir/ --include-regex='.*.xzx$'
        onlycopy_tester('onlycopy', noresults=True, validation_file='test_onlycopy_regex_filter_everything.txt',
                        arg_src_regex='.*.xzx$', arg_dst_regex='.*.xzx$')

    def test_onlycopy_regex_filter_but_has_results(self):
        """ test onlycopy regex so that is filters out some results but has results """
        # filegardener onlycopy --srcdir=test_data/onlycopy/firstdir/ test_data/onlycopy/seconddir/ --include-regex='.*.(png|xzx)$'
        onlycopy_tester('onlycopy', noresults=False, validation_file='test_onlycopy_regex_filter_but_has_results.txt',
                        arg_src_regex='.*.(png|xzx)$', arg_dst_regex='.*.(png|xzx)$')

    def test_onlycopy_regex_src_all_output(self):
        """ test only copy regex so that all files will be onlycopy files """
        # filegardener onlycopy --srcdir=test_data/identicaldirs/firstdir/ test_data/identicaldirs/seconddir/ --include-src-regex='.*.xzx$'
        onlycopy_tester('identicaldirs', noresults=False, validation_file='test_onlycopy_regex_src_all_output.txt',
                        arg_src_regex='.*.xzx$', arg_dst_regex=None)

    def test_onlycopy_regex_dst_rmonlycopy_files(self):
        """ test only copy regex so that only copy files are removed aka no results"""
        # filegardener onlycopy --srcdir=test_data/onlycopy/firstdir/ test_data/onlycopy/seconddir/ --include-dst-regex='.*.xzx$'
        onlycopy_tester('onlycopy', noresults=True, validation_file='test_onlycopy_regex_dst_rmonlycopy_files.txt',
                        arg_src_regex=None, arg_dst_regex='.*.xzx$')

    def test_onlycopy_regex_dst_has_onlycopy_files(self):
        """ test only copy regex so that only copy files are still present in results """
        # filegardener onlycopy --srcdir=test_data/onlycopy/firstdir/ test_data/onlycopy/seconddir/  --include-dst-regex='.*.png$'
        onlycopy_tester('onlycopy', noresults=False, validation_file='test_onlycopy_regex_dst_has_onlycopy_files.txt',
                        arg_src_regex='.*.png$', arg_dst_regex='.*.png$')

    @pytest.mark.parametrize('regex_arg', ['--include-regex=\'[].*\.txt$\'', '--include-src-regex=\'[].*\.txt$\'',
                                           '--include-dst-regex=\'[].*\.txt$\''])
    def test_fail_onlycopy_invalid_regex(self, regex_arg):
        """ This test validates that the onlycopy command will fail when given a bad regex argument """
        runner = CliRunner()
        test_dir = 'identicaldirs'

        base_tmpdir_src_filebase = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'firstdir'))
        base_tmpdir_dst_filebase = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'seconddir'))

        # filegardener onlycopy - s ~ / Desktop /./ tmp / --include - regex = '[].*\.txt$'
        result = runner.invoke(filegardener.cli, ['onlycopy', '--srcdir=' + base_tmpdir_src_filebase, base_tmpdir_dst_filebase, regex_arg])

        assert result.exit_code == 2

    def test_onlycopy_cli_filter_everything(self):
        """ test onlycopy regex so that it filters out all results even when it would have some with out the regex"""
        # filegardener onlycopy --srcdir=test_data/onlycopy/firstdir/ test_data/onlycopy/seconddir/ --include-dst-regex='.*.xzx$'
        runner = CliRunner()
        test_dir = 'onlycopy'

        base_tmpdir_src_filebase = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'firstdir'))
        base_tmpdir_dst_filebase = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'seconddir'))

        result = runner.invoke(filegardener.cli,
                               ['onlycopy', '-r', '--srcdir=' + base_tmpdir_src_filebase, base_tmpdir_dst_filebase,
                                '--include-regex=\'.*.xzx$\''])
        result_string = ''
        assert result_string == result.output
        assert result.exit_code == 0

    def test_onlycopy_cli_override_src_dst_regex(self):
        """ test onlycopy regex so that it proves the overrides work for
         include-regex to prevent include-src-regex include-dst-regex"""
        # TODO active looking to fix
        # filegardener onlycopy --srcdir=test_data/onlycopy/firstdir/ test_data/onlycopy/seconddir/ --include-dst-regex='.*.png$'
        runner = CliRunner()
        test_dir = 'onlycopy'

        base_tmpdir_src_filebase = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'firstdir'))
        base_tmpdir_dst_filebase = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'seconddir'))
        cli_cmd = ['onlycopy', '-r', '--srcdir=' + base_tmpdir_src_filebase, base_tmpdir_dst_filebase, '--include-regex'
                   , '.*.png$']
        result = runner.invoke(filegardener.cli, cli_cmd)
        result_string = 'test_data/onlycopy/seconddir/liten-0.1.5-py2.5/EGG-INFO/tumblr_static_70kt88zhd0so4g84koowgwow.png\n'
        assert result_string == result.output
        assert result.exit_code == 0

    def test_srcfile_cli_abs_path(self):
        """
        test srcfile command to make sure it can return the abs path
        Command: filegardener srcfile -s test_data/7notemptydirs/main -s test_data/7notemptydirs/other 
        """
        # 1) get output
        #       a) append from yield
        #       b) get whole output
        # 2) get verification file
        #       a) if relative do nothing
        #       b) if abs update to be abs
        # 3) compare output to verification

        # get output
        runner = CliRunner()
        test_dir = '7notemptydirs'

        base_tmpdir_src_filebase1 = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'main'))
        base_tmpdir_src_filebase2 = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'other'))
        cli_cmd = ['srcfile', '--srcdir=' + base_tmpdir_src_filebase1, '--srcdir=' + base_tmpdir_src_filebase2]
        result = runner.invoke(filegardener.cli, cli_cmd)
        # result.output
        # result.exit_code

        # get verification file
        # def check_output_against_validation_file(output, test_dir=None, validation_file=None,
        #                                 validation_absolute=True, result=True):
        check_output_against_validation_file(result.output, test_dir=test_dir, validation_file='test_srcfile_cli_abs_path.txt', abs_path_fn=srcfile_make_abs)

    def test_srcfile_cli_rel_path(self):
        """
        filegardener srcfile -r -s test_data/1dup/firstdir
        """
        runner = CliRunner()
        test_dir = '1dup'

        base_tmpdir_src_filebase1 = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'firstdir'))
        cli_cmd = ['srcfile', '--srcdir=' + base_tmpdir_src_filebase1, '-r']
        result = runner.invoke(filegardener.cli, cli_cmd)
        check_output_against_validation_file(result.output, test_dir=test_dir,
                                             validation_file='test_srcfile_cli_rel_path.txt',
                                             abs_path_fn=srcfile_make_abs,
                                             validation_absolute=False)

    def test_srcfile_cli_include_regex(self):
        """
        filegardener srcfile -r -s test_data/1dup/firstdir --include-regex '.*\.py'
        """
        runner = CliRunner()
        test_dir = '1dup'

        base_tmpdir_src_filebase1 = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'firstdir'))
        cli_cmd = ['srcfile', '--srcdir=' + base_tmpdir_src_filebase1, '-r', '--include-regex', '.*\.py']
        result = runner.invoke(filegardener.cli, cli_cmd)
        check_output_against_validation_file(result.output, test_dir=test_dir,
                                             validation_file='test_srcfile_cli_include_regex.txt',
                                             abs_path_fn=srcfile_make_abs,
                                             validation_absolute=False)

    def test_srcfile_abs_path(self):
        """
        filegardener srcfile -s test_data/1dup/firstdir
        """
        test_dir = '1dup'

        base_tmpdir_src_filebase1 = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'firstdir'))
        generator = filegardener.srcfile_yield([base_tmpdir_src_filebase1], failonerror=True, src_regex=None)
        check_output_against_validation_file(generator, test_dir=test_dir,
                                             validation_file='test_srcfile_abs_path.txt',
                                             abs_path_fn=srcfile_make_abs,
                                             validation_absolute=True, get_keyvalue_fn=srcfile_create_keyvalue)


    def test_srcfile_include_regex(self):
        """
        filegardener srcfile -r -s test_data/1dup/firstdir
        """
        test_dir = '1dup'

        base_tmpdir_src_filebase1 = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir, 'firstdir'))
        generator = filegardener.srcfile_yield([base_tmpdir_src_filebase1], failonerror=True, src_regex='.*\.py')
        check_output_against_validation_file(generator, test_dir=test_dir,
                                             validation_file='test_srcfile_include_regex.txt',
                                             abs_path_fn=srcfile_make_abs,
                                             validation_absolute=True, get_keyvalue_fn=srcfile_create_keyvalue)

    def test_srcfile_cli_bad_regex(self):
        """ This test validates that the srcfile command will fail when given a bad regex argument 
            Command: filegardener srcfile --srcfile=test_data/1dup/ --include-regex='[].*\.txt$' """
        runner = CliRunner()
        test_dir = '1dup'
        base_tmpdir_src_filebase = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
        result = runner.invoke(filegardener.cli, ['srcfile', '--srcdir=' + base_tmpdir_src_filebase, '--include-regex=\'[].*\.txt$\'' ])

        assert result.exit_code == 2

    def test_runner_with_hello_world(self):
        """ test onlycopy regex so that it proves the overrides work for
         include-regex to prevent include-src-regex include-dst-regex"""
        # filegardener onlycopy --srcdir=test_data/onlycopy/firstdir/ test_data/onlycopy/seconddir/ --include-dst-regex='.*.png$'
        runner = CliRunner()
        test_dir = 'onlycopy'

        cli_cmd = ['hello']
        result = runner.invoke(filegardener.cli, cli_cmd)

        assert result.output == 'world\n'
        assert result.exit_code == 0

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

    @pytest.fixture(scope='function')
    def file_dir_identicaldirs(self, request, tmpdir_factory):
        # tmpdir is a Reference: http://py.readthedocs.io/en/latest/path.html py.path.local object
        tmpdir = tmpdir_factory.mktemp('identicaldirs', numbered=True)
        def fin():
            print ("cleanup testing")
            # TODO: figure out how to access results to not to remove on failure
            # Reference: https://github.com/pytest-dev/pytest/blob/ffb583ae9140bfa14b28ff44245ec0b16ad760a7/doc/en/example/simple.rst
            tmpdir.remove(rec=1) # remove the directory if the test passes 
        request.addfinalizer(fin)
        return tmpdir

    def test_rmfiles_valid(self, file_dir_identicaldirs):
        runner = CliRunner()
        base_tmpdir = str(file_dir_identicaldirs) # string of full path to tmp dir
        test_dir = 'identicaldirs'
        test_data_dir = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
        base_tmpdir_dst = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir))
        base_tmpdir_dst_filebase = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir, 'seconddir'))
        file_of_items_to_remove = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir, 'correct_results.txt'))
        shutil.copytree(test_data_dir, base_tmpdir_dst)
        result = runner.invoke(filegardener.cli, ['rmfiles', '--basedir='+base_tmpdir, file_of_items_to_remove])
        #assert test_data_dir == base_tmpdir_dst
        
        count = filegardener.count_files({}, [base_tmpdir_dst_filebase])
        
        if result.exit_code != 0:
            print(result.output)
            
        assert result.exit_code == 0 and count == 0

    def test_rmfile_false_isdir(self, file_dir_identicaldirs):
        runner = CliRunner()
        base_tmpdir = str(file_dir_identicaldirs) # string of full path to tmp dir
        test_dir = 'identicaldirs'
        test_data_dir = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
        base_tmpdir_dst = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir))
        base_tmpdir_dst_filebase = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir, 'seconddir'))
        file_of_items_to_copy = os.path.abspath(os.path.join(test_data_dir, 'correct_results.txt'))
        shutil.copy(file_of_items_to_copy, base_tmpdir)
        result, reason = filegardener.rmfile(os.path.join(base_tmpdir))
        #assert test_data_dir == base_tmpdir_dst
            
        assert result == False and reason == "wasn't a file"
        
    def test_rmfile_false_isfile(self, file_dir_identicaldirs):
        runner = CliRunner()
        base_tmpdir = str(file_dir_identicaldirs) # string of full path to tmp dir
        test_dir = 'identicaldirs'
        test_data_dir = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
        base_tmpdir_dst = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir))
        base_tmpdir_dst_filebase = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir, 'seconddir'))
        file_of_items_to_copy = os.path.abspath(os.path.join(test_data_dir, 'correct_results.txt'))
        shutil.copy(file_of_items_to_copy, base_tmpdir)
        result, reason = filegardener.rmfile(os.path.join(base_tmpdir, 'correct_results.txt'))
        #assert test_data_dir == base_tmpdir_dst
        
        assert result == True and reason == None

    def test_rmfiles_1valid_file(self, file_dir_identicaldirs):
        runner = CliRunner()
        base_tmpdir = str(file_dir_identicaldirs) # string of full path to tmp dir
        test_dir = '1dup'
        test_data_dir = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
        base_tmpdir_dst = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir))
        base_tmpdir_dst_filebase = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir, 'seconddir'))
        file_of_items_to_remove = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir, 'correct_results.txt'))
        shutil.copytree(test_data_dir, base_tmpdir_dst)
        if not (os.path.exists(base_tmpdir_dst_filebase) and os.path.isdir(base_tmpdir_dst_filebase)):
            raise Exception("Dir should exist and doesn't")
        
        count_before = filegardener.count_files({}, [base_tmpdir_dst_filebase])
        
        result = runner.invoke(filegardener.cli, ['rmfiles', '--basedir='+base_tmpdir, file_of_items_to_remove])
        #assert test_data_dir == base_tmpdir_dst
        
        count_after = filegardener.count_files({}, [base_tmpdir_dst_filebase])
        
        if result.exit_code != 0:
            print(result.output)
            
        assert result.exit_code == 0 and (count_before - count_after) == 1
        
    def test_rmdirs_valid(self, file_dir_identicaldirs):
        runner = CliRunner()
        base_tmpdir = str(file_dir_identicaldirs) # string of full path to tmp dir
        test_dir = 'emptydirs'
        test_data_dir = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
        base_tmpdir_dst = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir))
        base_tmpdir_dst_filebase = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir, 'seconddir'))
        file_of_items_to_remove = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir, 'emptydirs_correct_results.txt'))
        shutil.copytree(test_data_dir, base_tmpdir_dst)
        result = runner.invoke(filegardener.cli, ['rmdirs', '--basedir='+base_tmpdir, file_of_items_to_remove])
        #assert test_data_dir == base_tmpdir_dst
        
        count = filegardener.count_dirs({}, [base_tmpdir_dst_filebase])
        
        if result.exit_code != 0:
            print(result.output)
            
        assert result.exit_code == 0 and count == 0

    def test_rmdirs_7notemptydirs(self, file_dir_identicaldirs):
        runner = CliRunner()
        base_tmpdir = str(file_dir_identicaldirs) # string of full path to tmp dir
        test_dir = '7notemptydirs'
        test_data_dir = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
        base_tmpdir_dst = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir))
        file_of_items_to_remove = os.path.abspath(os.path.join(base_tmpdir, 'test_data', test_dir, 'emptydirs_correct_results.txt'))
        shutil.copytree(test_data_dir, base_tmpdir_dst)
        if not (os.path.exists(base_tmpdir_dst) and os.path.isdir(base_tmpdir_dst)):
            raise Exception("Dir should exist and doesn't")
        
        count_before = filegardener.count_dirs({}, [base_tmpdir_dst])
        
        result = runner.invoke(filegardener.cli, ['rmdirs', '--basedir='+base_tmpdir, file_of_items_to_remove])
        #assert test_data_dir == base_tmpdir_dst
        
        count_after = filegardener.count_dirs({}, [base_tmpdir_dst])
        
        if result.exit_code != 0:
            print(result.output)
        
        # will have 9 dirs removed
        
        assert result.exit_code == 0 and (count_before - count_after) == 9

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
    """ you give this method a path name and it looks under test_data/ for that directory to test.  
    This test assumes that the order the duplicates will be found will be the same"""
    test_basedir = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
    validation_file_name = ''
    dir1 = os.path.join(test_basedir, 'firstdir')
    dir2 = os.path.join(test_basedir, 'seconddir')
    if reverse: 
        validation_file_name = 'correct_results_reverse_input_dirs.txt'
        srcdir = [dir2]
        checkdir = [dir1]
    else:
        validation_file_name = 'correct_results.txt'
        srcdir = [dir1]
        checkdir = [dir2]
        
    test_validation_file = os.path.join(test_basedir, validation_file_name)
    generator = filegardener.dedup_yield(srcdir, checkdir)
    
    if noresults:
        with pytest.raises(StopIteration):
            next(generator)
    else:
        with open(test_validation_file) as f:
            result_lookup = {}
            for line in f:
                file_name = line.rstrip()  # remove new lines from each line
                file_name = os.path.abspath(os.path.join(os.getcwd(), file_name))
                result_lookup[file_name] = file_name
            for line in generator:
                assert result_lookup[line] == line
                del result_lookup[line]
            assert len(result_lookup.keys()) == 0


def path_make_abs(path):
    return os.path.abspath(os.path.join(os.getcwd(), path))


def srcfile_make_abs(size_path):
    size, path = size_path.split(':', 2)
    return "{}:{}".format(size,os.path.abspath(os.path.join(os.getcwd(), path)))


def srcfile_create_keyvalue(file_size_tuple):
    return "{}:{}".format(file_size_tuple[1], file_size_tuple[0])


def check_output_against_validation_file(output, test_dir=None, validation_file=None,
                                         validation_absolute=True, result=True, abs_path_fn=path_make_abs, get_keyvalue_fn=None):
    """ srcfile test you give this method a output to verify and test_data/ for that directory to test.  
    This test assumes that the order the duplicates will be found will be the same
    output is expected to be a string or assumed to be a generator
    test_dir should be a dir in test_data of the project main
    validation_file should be a file in test_dir or a absolute path to a file
    validation_absolute boolean tells if a validation file should be converted to absolute paths for
        comparison to the output results. (default True)
    result if the function should expect results.
    """
    test_basedir = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
    test_validation_file = ''

    assert output is not None
    assert validation_file is not None

    if os.path.isfile(validation_file):
        test_validation_file = validation_file
    else:
        test_validation_file = os.path.join(test_basedir, validation_file)

    # check that the validation file points to a real file
    assert os.path.isfile(test_validation_file)

    if result:
        generator = None

        # turn your string output into generator
        if isinstance(output, str) or isinstance(output, unicode):
            generator = iter(output.splitlines())
        else:
            generator = output

        is_unicode_class = True
        try:
            unicode
        except:
            is_unicode_class = False

        convert_string = None

        if is_unicode_class:
            def convert_string_fn(my_string):
                return my_string.decode()

            convert_string = convert_string_fn
        else:
            def convert_string_fn(my_string):
                return my_string

            convert_string = convert_string_fn

        # open validation file
        # read every line stripping newline and turning file path into absolute path is necessary
        # store each line/filename as the key and value in a dictionary to be used for comparison
        # against the results
        with open(test_validation_file) as f:
            result_lookup = {}
            for line in f:
                file_name = line.rstrip()  # remove new lines from each line
                if validation_absolute:
                    file_name = abs_path_fn(file_name)
                # needs to be put here because abs_path_fn functions convert back to str
                if isinstance(file_name, str):
                    file_name = convert_string(file_name)
                result_lookup[file_name] = file_name
            for line in generator:
                # used so that the return value of the generator can be extracted
                # in a custom fashion
                if get_keyvalue_fn is not None:
                    line = get_keyvalue_fn(line)
                if isinstance(line, str):
                    line = line.decode()
                assert result_lookup[line] == line
                del result_lookup[line]
            assert len(result_lookup.keys()) == 0
    else:
        # you expect no result so your testing if that's true
        # is output is None okay
        # if a string empty is okay
        # otherwise assume it's a generator and should return no results

        # This unicode workaround for python 2 and 3 compatibility
        is_unicode_class = True
        try:
            unicode
        except:
            is_unicode_class = False

        is_string = None

        if is_unicode_class:
            def is_string_fn(my_string):
                return isinstance(my_string, str) or isinstance(output, unicode)

            is_string = is_string_fn
        else:
            def is_string_fn(my_string):
                return isinstance(my_string, str)

            is_string = is_string_fn

        if output is None:
            assert True
        elif is_string(output) and output == '':
            assert True
        else:
            with pytest.raises(StopIteration):
                next(generator)

def onlycopy_tester(test_dir, reverse=False, noresults=False, validation_file=None, arg_src_regex=None,
                    arg_dst_regex=None):
    """ onlycopy test you give this method a path name and it looks under test_data/ for that directory to test.  
    This test assumes that the order the duplicates will be found will be the same"""
    test_basedir = os.path.abspath(os.path.join(os.getcwd(), 'test_data', test_dir))
    validation_file_name = ''
    dir1 = os.path.join(test_basedir, 'firstdir')
    dir2 = os.path.join(test_basedir, 'seconddir')
    if reverse: 
        validation_file_name = 'onlycopy_correct_results_reverse_input_dirs.txt'
        srcdir = [dir2]
        checkdir = [dir1]
    else:
        validation_file_name = 'onlycopy_correct_results.txt'
        srcdir = [dir1]
        checkdir = [dir2]

    if validation_file is not None:
        validation_file_name = validation_file
        
    test_validation_file = os.path.join(test_basedir, validation_file_name)
    generator = filegardener.onlycopy_yield(srcdir, checkdir, src_regex=arg_src_regex, dst_regex=arg_dst_regex)
    
    if noresults:
        with pytest.raises(StopIteration):
            next(generator)
    else:
        with open(test_validation_file) as f:
            result_lookup = {}
            for line in f:
                file_name = line.rstrip()  # remove new lines from each line
                file_name = os.path.abspath(os.path.join(os.getcwd(), file_name))
                result_lookup[file_name] = file_name
            for line in generator:
                assert result_lookup[line] == line
                del result_lookup[line]
            assert len(result_lookup.keys()) == 0


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
            result_lookup = {}
            for line in f:
                file_name = line.rstrip() # remove new lines from each line
                file_name = os.path.abspath(os.path.join(os.getcwd(), file_name))
                result_lookup[file_name] = file_name
            for line in generator:
                assert result_lookup[line] == line
                del result_lookup[line]
            assert len(result_lookup.keys()) == 0

