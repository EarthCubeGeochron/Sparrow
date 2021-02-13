#!/bin/bash

install_path=${SPARROW_INSTALL_PATH:-${INSTALL_PATH:-/usr/local}}
build_dir=_cli/dist/sparrow
dist_dir=${1:-$install_path/opt/sparrow}
symlink=${2:-$install_path/bin/sparrow}
executable=${dist_dir}/sparrow

mkdir -p $dist_dir

echo "Downloading sparrow executable"
curl -L -s https://github.com/EarthCubeGeochron/Sparrow/releases/download/v2.0.0-alpha.11/sparrow-Darwin-x86_64.tar.gz \
| tar xvf - -C $dist_dir 2&>/dev/null

# Link executable onto the path
echo "Linking $symlink -> $executable"
ln -sf "$executable" "$symlink"

echo "Sparrow executable installed!"
echo "Check if you can run the 'sparrow' command. If not, you may need to add '$install_path/bin' to your PATH"
