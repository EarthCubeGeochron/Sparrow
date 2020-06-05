all: build

# Some information on how to build can be found at https://github.com/docker/compose

# Build the sparrow command-line application

_cli/dist/macos/sparrow:
	# Due to the vagaries of PyInstaller, Mac distribution must be built on OS X
	cd _cli && pyinstaller --distpath dist/macos sparrow.spec

_cli/dist/linux/sparrow:
	docker run -v "$(shell pwd)/_cli:/src" cdrx/pyinstaller-linux:latest

_cli/dist/windows/sparrow:
	docker run -v "$(shell pwd)/_cli:/src" cdrx/pyinstaller-windows:latest

# Build locally for the current platform
_cli/dist/sparrow: _cli/main.py
	_cli/_scripts/build-dist

build: _cli/dist/sparrow

_generate_buildspec:
	docker run -v "$(shell pwd)/_cli/:/src/" cdrx/pyinstaller-linux "pyinstaller main.py"

install: _cli/dist/sparrow
	_cli/_scripts/install

install-dev:
	_cli/_scripts/build-local
	-rm /usr/local/bin/sparrow
	ln -s $(shell pwd)/_cli/main.py /usr/local/bin/sparrow
