# Variables
VENV		   = venv
SYSTEM_PYTHON  = $(or $(shell which python3), $(shell which python))
PYTHON	   = $(or $(wildcard $(VENV_PYTHON)), $(SYSTEM_PYTHON))

.PHONY: all venv clean

# default target, when make executed without arguments
all: help

# Colors for echos 
ccend = $(shell tput sgr0)
ccbold = $(shell tput bold)
ccgreen = $(shell tput setaf 2)
ccso = $(shell tput smso)

setup: ## >> Setup a new virtual environment
	@echo ""
	@echo "$(ccso)--> Removing old virtual environment $(ccend)"
	rm -rf $(VENV)
	@echo "$(ccso)--> Setup virtual environment on $(VENV) $(ccend)"
	$(SYSTEM_PYTHON) -m venv $(VENV)

deps: requirements.txt	## >> Install dependencies in venv
	@echo "$(ccso)--> Installing Dependencies $(ccend)"
	# . venv/bin/activate; pip install -r requirements.txt
	./$(VENV)/bin/pip install -r requirements.txt
	@echo "$(ccso)--> Installing Dev-Dependencies $(ccend)"
	./$(VENV)/bin/pip install -r requirements-dev.txt

lint: ## >> Run Linters
	@echo ""
	@echo "$(ccso)--> Checking Lint $(ccend)"
	# pylint $$(git ls-files '*.py')
	pylint $$(ls -R *.py)
	@echo "$(ccso)--> Checking Flake8 $(ccend)"
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --statistics

test: ## >> Run Tests
	@echo ""
	@echo "$(ccso)--> Running tests $(ccend)"
	pytest

# And add help text after each target name starting with '\#\#'
# A category can be added with @category
HELP_FUN = \
	%help; \
	while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-\$\(]+)\s*:.*\#\#(?:@([a-zA-Z\-\)]+))?\s(.*)$$/ }; \
	print "usage: make [option]\n\n"; \
	for (sort keys %help) { \
	print "${WHITE}$$_:${RESET}\n"; \
	for (@{$$help{$$_}}) { \
	$$sep = " " x (32 - length $$_->[0]); \
	print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
	}; \
	print "\n"; }

help: ##@other >> Show this help.
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)
	@echo ""
	@echo "Note: to activate the environment in your local shell type:"
	@echo "   $$ source $(VENV)/bin/activate"
