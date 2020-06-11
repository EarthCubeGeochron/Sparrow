INSTALL_PATH ?= /usr/local
SPARROW_INSTALL_PATH ?= $(INSTALL_PATH)

all: build

build: _cli/dist/sparrow

# Bundle with PyInstaller and install (requires local Python 3)
install: _cli/dist/sparrow
	_cli/_scripts/install

# Install without building with PyInstaller
install-dev:
	_cli/_scripts/build-local
	mkdir -p $(SPARROW_INSTALL_PATH)/bin
	ln -sf $(shell pwd)/bin/sparrow $(SPARROW_INSTALL_PATH)/bin/sparrow

# Fallback Docker build instructions (for e.g. CI)
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
_cli/dist/sparrow: _cli/main.py
	_cli/_scripts/build-dist

_generate_buildspec:
	docker run -v "$(shell pwd)/_cli/:/src/" cdrx/pyinstaller-linux "pyinstaller main.py"
