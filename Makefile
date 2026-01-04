default: help

.PHONY: help
help: # Show help for each of the Makefile recipes. (This was yoinked from https://dwmkerr.com/makefile-help-command/)
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | while read -r l; do printf "\033[1;32m$$(echo $$l | cut -f 1 -d':')\033[00m:$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: up
up: # Start the development environment
	ddev start

.PHONY: down
down: # Stop the development environment
	ddev stop

.PHONY: install
install: # Install dependencies
	ddev npm install

.PHONY: watch
watch: # Watch for changes
	ddev npm run watch