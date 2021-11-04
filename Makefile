INSTALL_PATH ?= /usr/local
SPARROW_INSTALL_PATH ?= $(INSTALL_PATH)

all: install-hooks build-dev

build:
	_cli/_scripts/build-dist

# Install locally-built executable. There should be no links preserved to the source
# code after that
install: build install-dist

# Development installation
build-dev:
	_cli/_scripts/build-local

# Install without building with PyInstaller
install-dev: build-dev
	mkdir -p $(SPARROW_INSTALL_PATH)/bin
	ln -sf $(shell pwd)/_cli/sparrow-dev-shim $(SPARROW_INSTALL_PATH)/bin/sparrow

## TODO: fix bugs with install-dist to make it more capable
# Bundle with PyInstaller and install (requires local Python 3)
install-dist: install-hooks
	./get-sparrow.sh _cli/dist/sparrow

test:
	_cli/_scripts/test-cli

clean:
	rm -rf _cli/build

.PHONY: build install install-dev build-dev install-dist test clean

# Docker CLI build instructions (for e.g. CI)
# Some information on how to build can be found at https://github.com/docker/compose
# Build the sparrow command-line application (for different platforms)

_cli/dist/macos/sparrow:
	# Due to the vagaries of PyInstaller, Mac distribution must be built on OS X
	pyinstaller --distpath _cli/dist/macos _cli/sparrow.spec

# Build locally for the current platform (DEFAULT)
_cli/dist/sparrow:
	_cli/_scripts/build-dist

build-linux:
	docker run \
		-v "$(shell pwd):/src/" \
		cdrx/pyinstaller-linux:latest \
		_cli/_scripts/build-dist

# This will build the CLI for windows, which is currently unsupported
# (WSL integration with the linux binaries should be used instead)
build-windows:
	docker run \
		-v "$(shell pwd):/src/" \
		cdrx/pyinstaller-windows:latest \
		_cli/_scripts/build-dist

# Helper to generate a build specification
_generate_buildspec:
	cd _cli && \
	pyinstaller --noconfirm --distpath dist sparrow_cli/__main__.py

# Link git hooks
# (handles automatic submodule updating etc.)
# For git > 2.9
install-hooks:
	git config --local core.hooksPath .githooks
	# Always git prune on config
	git config --local remote.origin.prune true
	# Initialize submodules if we haven't already
	-[ ! -d .git/modules ] && git submodule update --init

format-code:
	black backend/**/*.py _cli/**/*.py
	prettier --ignore-path frontend/.prettierignore --write frontend