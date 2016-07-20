# coding: utf-8
""" This module is the first test module"""
import pytest
import filegardener


class TestBasics(object):
    """
    This class could have been called anything and can have second class here
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """
        Here is where things get setup
        """
        asdf = 1 + 1
        asdf = asdf + 2


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

    @pytest.mark.parametrize(
        'other, result', (
            ("some string", True),
            ("another string", True)
        )
    )
    def test_paramertrize_example(self, other, result):
        """ Example of using parameters to make multiple call """
        assert (other == other) is result
