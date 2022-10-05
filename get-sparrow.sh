#!/bin/bash

# https://gist.github.com/lukechilds/a83e1d7127b78fef38c2914c4ececc3c
get_release() {
  curl --silent "https://api.github.com/repos/$1/releases/${2:-latest}" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

get_latest_prerelease() {
  curl --silent "https://api.github.com/repos/$1/releases" | # Get latest release from GitHub api
    grep '"tag_name":' |  # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/' |  # Pluck JSON value
    head -n 1
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

should_confirm=1
if [ "$1" == "--no-confirm" ]; then
  should_confirm=0
  shift
fi

# Check whether we should install prereleases
if [ "$1" == "--prerelease" ]; then
  prerelease=1
  shift
else
  prerelease=0
fi

repo_name=EarthCubeGeochron/Sparrow

platform=$(uname -s)
header "Installing Sparrow on $platform"
line

# Get the version of Sparrow to install, either from the user or
# the latest tagged release on GitHub

# Release should be last argument to the script if provided
release="$1"
local_install=0
if [ -z $release ]; then
  header "Finding latest Sparrow release"
  # Check if prereleases are allowed
  if [ $prerelease -eq 1 ]; then
    detail "Prereleases allowed"
    release=$(get_latest_prerelease $repo_name)
  else
    release=$(get_release $repo_name latest)
  fi
  detail "found release $release"
elif [ -d $release ]; then
  detail "Installing local file $release"
  local_install=1
else
  header "Finding user-specified version $release"
fi
line


url=https://github.com/$repo_name/releases/download/$release/sparrow-$platform-x86_64.tar.gz

install_path=${SPARROW_INSTALL_PATH:-${INSTALL_PATH:-/usr/local}}
build_dir=_cli/dist/sparrow
dist_dir=${SPARROW_DIST_DIR:-$install_path/opt/sparrow}
symlink=$install_path/bin/sparrow
#TMPDIR=$install_path/sparrowtemp

# We now use the download script for local installations as well, because there
# is a ton of logic around where to install the source root for the Sparrow codebase.
# This may be something we can get rid of eventually, or wrap into the CLI itself.
if ((!local_install)); then
  # Check whether URL exists
  header "Checking download link"
  detail "\e[2m$url\e[0m"
  if curl --output /dev/null --silent --head --fail "$url"; then
    detail "link is accessible!"
  else
    abort "could not access link!"
  fi
  detail ""
fi

header "Installation prefix:\e[0m $install_path"
line "\e[0m"

if [[ $platform == "Darwin" && ! $dist_dir == /Users* ]]; then
  header "Adjustments for MacOS"
  d4m="\e[2m\e[1mDocker for Mac\e[0m\e[2m"
  detail "$d4m can only mount volumes in certain directories."
  if [[ $dist_dir == /usr/local/opt/sparrow ]]; then
    dist_dir=$HOME/.sparrow/opt
    detail "\e[2mThe SPARROW_DIST_DIR has been changed to $dist_dir"
    detail "to conform to these requirements."
  else
    detail "\e[2mYou specified a non-standard installation path outside of the \e[0m/Users\e[2m directory."
    detail "\e[0m\e[1m\e[31mThis may not work!!!\e[0m"
    detail "\e[2mPlease ensure that $d4m has permissions to mount volumes in your SPARROW_DIST_DIR."
  fi
  detail "\e[2mSee https://github.com/EarthCubeGeochron/Sparrow/issues/210 for more information."
  line "\e[0m"
fi

header "The following locations will be overwritten:"
detail "\e[2m\e[1mTip:\e[0m\e[2m These can be adjusted using environment variables.\e[0m"
bullet "$symlink \e[2m(Adjust using SPARROW_INSTALL_PATH or INSTALL_PATH)\e[0m"
bullet "$dist_dir \e[2m(Adjust using SPARROW_DIST_DIR)"
line "\e[0m"

executable=$dist_dir/sparrow

#check permissions
# if permissions are needed it will notify and attempy a sudo login
SUDO=""
if ! [ -w $install_path ]; then
    header "Permissions"
    detail "Elevated permissions are required to install to $install_path."
    detail "You may be prompted for your password."
    line
fi

if ((should_confirm)); then
  line "Would you like to continue? (y/N)"
  read -r answer
  if [[ $answer == "y" || $answer == "Y" || $answer == "yes" || $answer == "Yes" ]]
  then
    line
  else
    abort "Installation cancelled"
  fi
else
  line "Skipping confirmation..."
fi

SUDO=""
if ! [ -w $install_path ]; then
    sudo bash -c "echo ''" || abort "no permissions granted."
    SUDO="sudo"
fi

source_dir=""
if ((local_install)); then
  header "Installing Sparrow from local file"
  source_dir=$release
else
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

  source_dir=$temp_dir
fi


line "clearing out $dist_dir"
$SUDO rm -rf $dist_dir
$SUDO mkdir -p $dist_dir
## Move files to the correct directory
# and test they have successfully moved
line "installing to $dist_dir"

# We could do something bad here if source dir was unset!
if [ -z $source_dir ]; then
  abort "source_dir not set"
fi

if ((local_install)); then
  $SUDO cp -r $source_dir/* $dist_dir
else
  $SUDO mv $temp_dir/* $dist_dir
fi

move_test_file=$dist_dir/sparrow

if [ ! -z $temp_dir ]; then
  detail "deleting $temp_dir"
  rm -rf $temp_dir
fi

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
