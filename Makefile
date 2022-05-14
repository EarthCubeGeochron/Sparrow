INSTALL_PATH ?= /usr/local
SPARROW_INSTALL_PATH ?= $(INSTALL_PATH)

.PHONY: build install install-dev build-dev install-dist test clean

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
	ln -sf "$(shell pwd)/_cli/sparrow-dev-shim" "$(SPARROW_INSTALL_PATH)/bin/sparrow"

## TODO: fix bugs with install-dist to make it more capable
# Bundle with PyInstaller and install (requires local Python 3)
install-dist: install-hooks
	_cli/_scripts/build-dist
	./get-sparrow.sh --no-confirm _cli/build/sparrow

test:
	_cli/_scripts/test-cli

clean:
	rm -rf _cli/build

# Build locally for the current platform (DEFAULT)
_cli/build/sparrow:
	_cli/_scripts/build-dist

# For older varieties of Linux, we have to build in a Docker container
# with an older libc. This is mostly an issue for RHEL and older Ubuntu installations.
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