#!/usr/bin/env bash
# Updates the version from version.txt acorss the python packages and such

VERSION=$(cat version.txt)
VERSION_STR="__version__ = \"$VERSION\""

echo $VERSION_STR > ./src/CubeServer-app/cubeserver_app/_version.py
echo $VERSION_STR > ./src/CubeServer-api/cubeserver_api/_version.py
echo $VERSION_STR > ./src/CubeServer-common/cubeserver_common/_version.py
