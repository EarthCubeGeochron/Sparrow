#!/bin/bash

# https://gist.github.com/lukechilds/a83e1d7127b78fef38c2914c4ececc3c
get_latest_release() {
  curl --silent "https://api.github.com/repos/$1/releases/latest" | # Get latest release from GitHub api
    grep '"tag_name":' |                                            # Get tag line
    sed -E 's/.*"([^"]+)".*/\1/'                                    # Pluck JSON value
}

abort() {
    echo $1

    echo "aborting..."
    exit
}

################################################################### script

repo_name=EarthCubeGeochron/Sparrow
version=${1:-$(get_latest_release $repo_name)}
platform=$(uname -s)

url=https://github.com/$repo_name/releases/download/$version/sparrow-$platform-x86_64.tar.gz

install_path=${SPARROW_INSTALL_PATH:-${INSTALL_PATH:-/usr/local}}
build_dir=_cli/dist/sparrow
dist_dir=$install_path/opt/sparrow
symlink=$install_path/bin/sparrow
executable=$dist_dir/sparrow
#TMPDIR=$install_path/sparrowtemp

#check permissions
# if permissions are needed it will notify and attempy a sudo login
SUDO=""
if ! [ -w $install_path ]
then
    echo "Elevated permissions are required to install to $install_path."
    echo "If you choose to continue you may be prompted for your password."
    echo "Would you like to continue? (y/N)"
    read answer
    if [[ $answer == "y" || $answer == "Y" || $answer == "yes" || $answer == "Yes" ]]
    then
        sudo bash -c "echo ''"
        SUDO="sudo"
    else 
        abort "No permissions granted."
        echo ""
    fi
fi


## create temporary directory using the TMPDIR environmental variable
temp_dir=$(mktemp -d)
if [ ! -d $temp_dir ]; then
  echo "$temp_dir not created successfully"
  exit 1
fi

## check header to make sure url exists
if [ $(curl -I -s ${url} | grep -c "Not Found") -eq 1 ]
then 
    abort "${url} not found"
fi

## download into temp directory to see if it downloaded correctly
echo "Downloading Sparrow CLI $version"
curl -L -s ${url} | $SUDO tar xzf - -C $temp_dir

test_file=$temp_dir/sparrow

if [ -f "$test_file" ]; then
  echo "...success!"
else
  abort "..download unsuccessful"
fi

echo ""

$SUDO rm -rf $dist_dir
$SUDO mkdir -p $dist_dir
## Move files to the correct directory
# and test they have successfully moved
echo "Installing to $dist_dir"
$SUDO mv $temp_dir/* $dist_dir

move_test_file=$dist_dir/sparrow

if [ -f "$move_test_file" ]; 
then
    rm -rf ${temp_dir}
    echo "...success!"
else
    rm -rf ${temp_dir}
    abort "...copying unsuccessful"
fi

echo ""

$SUDO mkdir -p $install_path/bin
# Link executable onto the path
echo "Linking $symlink -> $executable"
$SUDO ln -sf "$executable" "$symlink"

echo "...Sparrow executable installed!"
echo ""
echo "Check if you can run the 'sparrow' command. If not, you may need to add '$install_path/bin' to your PATH"
