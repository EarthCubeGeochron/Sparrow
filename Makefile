INSTALL_PATH ?= /usr/local
SPARROW_INSTALL_PATH ?= $(INSTALL_PATH)

all: install-hooks build

build:
	_cli/_scripts/build-local

# Install without building with PyInstaller
install: build
	mkdir -p $(SPARROW_INSTALL_PATH)/bin
	sudo ln -sf $(shell pwd)/_cli/sparrow-dev-shim $(SPARROW_INSTALL_PATH)/bin/sparrow

install-dev: install

## TODO: fix bugs with install-dist to make it more capable
# Bundle with PyInstaller and install (requires local Python 3)
install-dist: _cli/dist/sparrow install-hooks
	_cli/_scripts/install

test:
	_cli/_scripts/test-cli

# Docker CLI build instructions (for e.g. CI)
# Some information on how to build can be found at https://github.com/docker/compose
# Build the sparrow command-line application (for different platforms)

_cli/dist/macos/sparrow:
	# Due to the vagaries of PyInstaller, Mac distribution must be built on OS X
	pyinstaller --distpath _cli/dist/macos _cli/sparrow.spec

_cli/dist/linux/sparrow:
	docker run -v "$(shell pwd)/_cli:/src" cdrx/pyinstaller-linux:latest

_cli/dist/windows/sparrow:
	docker run -v "$(shell pwd)/_cli:/src" cdrx/pyinstaller-windows:latest

# Build locally for the current platform
_cli/dist/sparrow:
	_cli/_scripts/build-dist

_generate_buildspec:
	docker run -v "$(shell pwd)/_cli/:/src/" cdrx/pyinstaller-linux "pyinstaller main.py"

# Link git hooks
# (handles automatic submodule updating etc.)
# For git > 2.9
install-hooks:
	git config --local core.hooksPath .githooks
	# Always git prune on config
	git config --local remote.origin.prune true
