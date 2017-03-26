test: ## Run the unit tests
	python setup.py test	
	@echo ""
	# This runs all of the tests. To run an individual test, run py.test with
	# the -k flag, like "py.test -k test_path_is_not_double_encoded"
	@echo ""
	@echo "Alternative use pytest directly and install pytest and run the pytest runner"
	@# https://pytest.org/latest/goodpractices.html
	@echo "> py.test -v tests"

py.test:
	@which py.test || (echo "py.text is not installed: $$?\n Install:\n > pip install pytest pytest-cov"; exit 1)

setup: setup-py2 ## default setup uses setup-py2 - run dynamic target "make setup-py3" for python 3
	@# default setup uses setup-py2 - run dynamic target "make setup-py3" for python 3
	@echo "# Default is python2"
	@echo "# For python3"
	@echo "> make setup-py3"
	@# Test the version of 'virtualenv' you have installed because there are issues if it is too old
	@# print virutal env number, filter for line with 'Version' in it, split on colon and take second half, take first number 'major version', remove whitespace
	@# As of 11/2016 virtual env version is 15
	@VIRTUALENV_VERSION=$$(pip show -V virtualenv | grep Version | cut -f2 -d':' | cut -f1 -d'.' | sed 's/[[:blank:]]//g'); if [[ "$$VIRTUALENV_VERSION" != "x"  &&  "$$VIRTUALENV_VERSION" -lt  "12" ]] ; then echo "WARNING:your virtualenv is very old please update it 'pip install -U virtualenv'\n you should 'make clean-all', upgrade, then run 'make setup' again "; fi


# Using dynamic target to dynamically pick which variables are used
# This allows us to keep the rest common for the target

# command to create the py2 virtualenv
setup-py2-part1 := $(shell echo "virtualenv \$${FILEGARDENER_ENV:-.}/filegardener-virtualenv")
# source the virtual environment so it's active
setup-py2-part2 := $(shell echo ". \$${FILEGARDENER_ENV:-.}/filegardener-virtualenv/bin/activate")

# command to create the py2 virtualenv
setup-py3-part1 := $(shell echo "python3 -m venv \$$FILEGARDENER_ENV/filegardener-venv")
# source the virtual environment so it's active
setup-py3-part2 := $(shell echo ". \$${FILEGARDENER_ENV:-.}/filegardener-venv/bin/activate")


setup-%: # On macs will copy text to clipboard so you can just paste it
	@# print message in bold and red the reset text to normal 
	@echo `tput bold``tput setaf 1`"YOU MUST MANUALLY RUN:"`tput sgr0`
	@# print the command to create a virtualenv and put it in the $FILEGARDENER_ENV
	@echo "#Env variable FILEGARDENER_ENV (should be directory) if not set put it the current directory\n"
	@echo "\n Do your self a favor and install make file completions:"
	@echo "> brew install bash-completion"
	@echo "https://github.com/scop/bash-completion\n"
	@#  if [ -f $(brew --prefix)/etc/bash_completion ]; then
	@#    . $(brew --prefix)/etc/bash_completion
	@#  fi
	@echo "export FILEGARDENER_ENV=~/Desktop/"
	@echo "#if necessary run: pip install --upgrade pip"
	@# This prints the two dynamic variables, $@ is the dependency setup-[py2,py3]
	@echo "$($@-part1)\n$($@-part2)"
	@# Executes the bash in the variable
	@$($@-part1)
	@# If mac then copy code to clipboard
	@if [ "$$(uname)" == "Darwin" ]; then echo "\n"`tput bold``tput setaf 1`"auto-copied to clipboard just paste (Cmd v)"`tput sgr0`"\n" ; fi
	@if [ "$$(uname)" == "Darwin" ]; then echo "$($@-part1)\n$($@-part2)" | pbcopy ; fi

# variable to use for python 2 or python 3
load-venv-py2-part1 := $(shell echo ". \$${FILEGARDENER_ENV:-.}/filegardener-virtualenv/bin/activate")
load-venv-py3-part1 := $(shell echo ". \$${FILEGARDENER_ENV:-.}/filegardener-venv/bin/activate")

venv: load-venv ## alias for load-venv

load-venv: load-venv-py2 ## load the virtualenv for python 2 or python 3
	@echo "Using python 2"

load-venv-%: ## using py2 or py3 print or load command to load your virtualenv
	@# If mac then copy code to clipboard
	@echo `tput bold``tput setaf 1`"YOU MUST MANUALLY RUN:"`tput sgr0`
	@if [ "$$(uname)" == "Darwin" ]; then echo "\n"`tput bold``tput setaf 1`"auto-copied to clipboard just paste (Cmd v)"`tput sgr0`"\n" ; else  echo "run the following command" ; fi
	@if [ "$$(uname)" == "Darwin" ]; then echo "$($@-part1)" | pbcopy ; else echo "$($@-part1)" ; fi

install-local: ## installs as a local package TODO: better comment
	pip install --upgrade .

install-dev: ## installs editable in place so you can do development
	pip install -e .

init: install-requirements  ## install all requirements once

create-requirements: ## Creates a requirements file but you shouldn't need this when using setup.py
	pip freeze > requirements.txt
	
install-requirements: ## Installs a requirements file but you shouldn't need this when using setup.py
	pip install -r requirements.txt

list-packages: ## print the name of packages you can register
	@find tmp/dist -iname "*.tar.gz"
	@find tmp/wheelhouse -iname "*.whl"

publish: ## Publish/Register this package to production on PyPi
	@echo "list packages to register with: > make list-packages\n"
	@echo "> twine upload "$$(find tmp/dist -iname "*.tar.gz")
	@echo "> twine upload "$$(find tmp/wheelhouse -iname "*.whl")

.DEFAULT_GOAL := help

.PHONY: help

help:
	@echo "SYNOPSIS"
	@echo "     make command"
	@echo ""
	@echo "COMMANDS"
	@echo ""
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "QUICK START"
	@echo ""
	@echo "> make setup\n"
	@echo "     #creates a virtualenv" 
	@echo ""
	@echo "> make venv\n"
	@echo "     #loads your virtualenv" 
	@echo ""
	@echo "> make init\n"
	@echo "     #installs all your python requirements" 
	@echo ""
	@echo "> make install-dev\n"
	@echo "     #installs the project locally" 
	@echo ""
	@echo "> filegardener\n"
	@echo "     #now you can run filegardener"
	@echo ""
	@echo "RUN TESTS"
	@echo ""
	@echo "> make test\n"
	@echo "     #runs tests" 
	@echo ""
	@echo ""
	@echo "PUBLISH PROJECT"
	@echo ""
	@echo "> make build\n"
	@echo "     #builds the wheels for the project" 
	@echo ""
	@echo "> make publish\n"
	@echo "     #prints the commands you need to run to publish" 
	@echo ""

build: ## builds a setuptool sdist (source distribution and local wheel package) for filegardener
	@# Reference: https://packaging.python.org/distributing/#wheels
	@echo "remove symlinks that are created for testing before building"
	@# The '-' infront of the command has the makefile ignore errors if the files are already removed
	-rm test_data/onlycopysymfirst/firstdir/brokensymlink
	-rm test_data/onlycopysymfirst/firstdir/doesnotexist
	-rm test_data/onlycopysymsecond/seconddir/brokensymlink
	-rm test_data/onlycopysymsecond/seconddir/doesnotexist
	mkdir -p tmp/egg-info
	python setup.py -v egg_info --egg-base=./tmp/egg-info build --build-base=./tmp/build sdist --dist-dir=./tmp/dist bdist_wheel --verbose --dist-dir=./tmp/wheelhouse
	
build-exe: build ## builds a self contained python exe (doesn't include interpreter) platform specific
	@# Reference: https://pex.readthedocs.io
	pex -f ./tmp/wheelhouse  -e filegardener:cli -o ./tmp/bin/filegardener filegardener

clean: ## cleans up all dist files, build files AND NOT virtualenv
	rm -rf ./tmp
	rm -f ./filegardener.pyc
	rm -rf ./filegardener.egg-info
	rm -rf ./tests/__pycache__
	
clean-all: clean ## cleans up all dist files, build files AND virtualenv
	rm -rf $${FILEGARDENER_ENV:-.}/filegardener-virtualenv
	rm -f ./*.log
	
init-docs: ## You should only do this once
	if [ ! -d ./docs ] ; then sphinx-quickstart ; fi

generate-docs-html:  ## Generate documentation for the project in docs/_build/html/
	$(MAKE) -C docs html	

open-docs:  ## Tries to open the html docs in a browser
	@if [ "$$(uname)" == "Darwin" ]; then open docs/_build/html/index.html ; fi
	@if [ "$$(uname)" != "Darwin" ]; then echo "Not implemented for non-mac" ; fi

generate-testdirs: ## creates the DIRECTORIES.txt file from all directories in test_data
	invoke generate.testdirs
