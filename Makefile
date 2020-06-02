all: build

# Build the sparrow command-line application
build:
	docker run -v "$(shell pwd)/_cli:/src" cdrx/pyinstaller-linux:latest

spec:
	docker run -v "$(shell pwd)/_cli/:/src/" cdrx/pyinstaller-linux "pyinstaller --onefile main.py"
