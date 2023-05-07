#!/usr/bin/env bash
# Packages an API wrapper library with the client configuration,
# provided a git-clone-able url for the library's source, and the
# path to the client configuration.
#
# Usage: package_lib.sh [GIT URL] [CLIENT_CONFIG_FILE_PATH] [OUTPUT_PATH]
#

WORKING_DIR=/tmp/API-WRAPPER-$(echo $RANDOM | md5sum | head -c 16)/
mkdir -p $WORKING_DIR
cp $2 $WORKING_DIR/

cd $WORKING_DIR

git clone $1
cd "$(basename "$1" .git)"
cp ../"$(basename "$2")" ./lib/ || cp ../"$(basename "$2")" ./
mv "$(bash package.sh | tail -n1)" "$3"
cd /tmp
rm -r $WORKING_DIR
