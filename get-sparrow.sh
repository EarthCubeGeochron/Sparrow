#!/bin/bash

# https://gist.github.com/lukechilds/a83e1d7127b78fef38c2914c4ececc3c
get_latest_release() {
  curl --silent "https://api.github.com/repos/$1/releases/latest" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

repo_name=EarthCubeGeochron/Sparrow
platform=$(uname -s)
install_path=${SPARROW_INSTALL_PATH:-${INSTALL_PATH:-/usr/local}}
build_dir=_cli/dist/sparrow
dist_dir=$install_path/opt/sparrow
symlink=$install_path/bin/sparrow
executable=$dist_dir/sparrow

rm -r $dist_dir
mkdir -p $dist_dir

version=${1:-$(get_latest_release $repo_name)}

echo "Downloading Sparrow CLI $version"
curl -L -s https://github.com/$repo_name/releases/download/$version/sparrow-$platform-x86_64.tar.gz \
| tar xvf - -C $dist_dir 2&> /dev/null

# Link executable onto the path
echo "Linking $symlink -> $executable"
ln -sf "$executable" "$symlink"

echo "Sparrow executable installed!"
echo "Check if you can run the 'sparrow' command. If not, you may need to add '$install_path/bin' to your PATH"
