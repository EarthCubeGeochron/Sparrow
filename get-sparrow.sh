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
temp_path=$install_path/sparrowtemp

#check permissions
# if permissions are needed it will notify and attempy a sudo login
if ! [ -w $dist_dir ]
then
    echo "To install to path, we need to elevate permissions."
    echo "If you choose to continute you will be prompted for your password"
    echo "Would you like to continue? (y/N)"
    read answer
    if [[ $answer == "y" || $answer == "Y" || $answer == "yes" || $answer == "Yes" ]]
    then
        echo "Please enter your password."
        exec sudo bash "$0" "$@"
        echo
        echo
    else 
        abort "No permissions granted."
    fi
fi


rm -r $dist_dir
mkdir -p $dist_dir

rm -r $temp_path
mkdir -p $temp_path


## check header to make sure url exists
if [ `curl -I -s ${url} | grep -c "Not Found"` -eq 1 ]
then 
    abort "${url} not found"
fi

## download into temp directory to see if it downloaded correctly
echo "Downloading Sparrow CLI $version"
echo 
echo
curl -L -s ${url} | tar xzf - -C $temp_path

test_file=$temp_path/sparrow

if [ -f "$test_file" ]; then
        echo "You have successfully downloaded Sparrow!!"
        echo
        echo
    else
        abort "Download unsuccessful"
fi

## Move files to the correct directory
# and test they have successfully moved
mv $temp_path/* $dist_dir

move_test_file=$dist_dir/sparrow

if [ -f "$move_test_file" ]; 
then
    rm -r $temp_path
else
    abort "Problem when copying files"
fi



# Link executable onto the path
echo "Linking $symlink -> $executable"
ln -sf "$executable" "$symlink"

echo "Sparrow executable installed!"
echo "Check if you can run the 'sparrow' command. If not, you may need to add '$install_path/bin' to your PATH"
