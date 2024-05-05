default: help

.PHONY: help
help: # Show help for each of the Makefile recipes. (This was yoinked from https://dwmkerr.com/makefile-help-command/)
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: setup
setup: # Sets up a .venv and installs all needed packages
	python -m venv .venv
	.venv\Scripts\activate
	make install

.PHONY: install
install: # Runs pip install
	.venv\Scripts\pip install -r requirements.txt