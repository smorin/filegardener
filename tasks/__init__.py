""" tasks directory are tasks that can be executed using the invoke command of the pypi package invoke
basically will run any function with @task annotation
"""
import invoke

from . import generate

ns = invoke.Collection(generate)