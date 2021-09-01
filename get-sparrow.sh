#!/bin/bash

# https://gist.github.com/lukechilds/a83e1d7127b78fef38c2914c4ececc3c
get_release() {
  curl --silent "https://api.github.com/repos/$1/releases/${2:-latest}" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

line() {
  >&2 printf -- "$1\n"
}

header() {
  line "\e[1m$1\e[0m"
}

bullet() {
  line " - $1"
}

detail() {
  line "   $1"
}


abort() {
    detail "$1"
    detail "exiting"
    exit 1
}


################################################################### script

repo_name=EarthCubeGeochron/Sparrow

platform=$(uname -s)
header "Installing Sparrow on $platform"
line

# Get the version of Sparrow to install, either from the user or
# the latest tagged release on GitHub

# Release should be last argument to the script if provided
release="$1"
if [ -z $release ]; then
  header "Finding latest Sparrow release"
  release=$(get_release $repo_name latest)
  detail "found release $release"
else
  header "Finding user-specified version $release"
fi
line


url=https://github.com/$repo_name/releases/download/$release/sparrow-$platform-x86_64.tar.gz

install_path=${SPARROW_INSTALL_PATH:-${INSTALL_PATH:-/usr/local}}
build_dir=_cli/dist/sparrow
dist_dir=$install_path/opt/sparrow
symlink=$install_path/bin/sparrow
executable=$dist_dir/sparrow
#TMPDIR=$install_path/sparrowtemp

# Check whether URL exists
header "Checking download link"
detail "\e[2m$url\e[0m"
if curl --output /dev/null --silent --head --fail "$url"; then
  detail "link is accessible!"
else
  abort "could not access link!"
fi
detail ""

header "Installation prefix:\e[0m $install_path"
detail "\e[1m\e[2mTip:\e[0m \e[2mthe installation prefix can be controlled with the"
detail "\e[0mSPARROW_INSTALL_PATH\e[2m or \e[0mINSTALL_PATH\e[2m environment variables."
line "\e[0m"

header "The following locations will be written:"
bullet "$dist_dir"
bullet "$symlink"
line

#check permissions
# if permissions are needed it will notify and attempy a sudo login
SUDO=""
if ! [ -w $install_path ]; then
    header "Permissions"
    detail "Elevated permissions are required to install to $install_path."
    detail "You may be prompted for your password."
    line
fi

# Ask for confirmation no matter what
line "Would you like to continue? (y/N)"
read -r answer

if [[ $answer == "y" || $answer == "Y" || $answer == "yes" || $answer == "Yes" ]]
then
  line
else
  abort "Installation cancelled"
fi

SUDO=""
if ! [ -w $install_path ]; then
    sudo bash -c "echo ''" || abort "no permissions granted."
    SUDO="sudo"
fi


## create temporary directory using the TMPDIR environmental variable
temp_dir=$(mktemp -d)
if [ ! -d $temp_dir ]; then
  abort "$temp_dir not created successfully"
fi

## download into temp directory to see if it downloaded correctly
header "Downloading Sparrow CLI \e[0m$release"
curl -L -s ${url} | $SUDO tar xzf - -C $temp_dir

test_file=$temp_dir/sparrow

if [ -f "$test_file" ]; then
  detail "success!"
else
  abort "download unsuccessful"
fi
line

line "clearing out $dist_dir"
$SUDO rm -rf $dist_dir
$SUDO mkdir -p $dist_dir
## Move files to the correct directory
# and test they have successfully moved
line "installing to $dist_dir"
$SUDO mv $temp_dir/* $dist_dir

move_test_file=$dist_dir/sparrow

rm -rf $temp_dir
if [ -f "$move_test_file" ]; 
then
    detail "success!"
else
    abort "copying unsuccessful"
fi

line

$SUDO mkdir -p $install_path/bin
# Link executable onto the path
line "Linking $symlink"
line "     -> $executable"
$SUDO ln -sf "$executable" "$symlink"
line

header "\e[32mSparrow executable installed!\e[0m"
line
header "\e[2mNext steps:\e[0m"
line "\e[2mCheck if you can run the 'sparrow' command. If not, you may need"
line "to add $install_path/bin to your PATH"
