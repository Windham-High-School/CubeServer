#!/usr/bin/env bash
# Updates the version from version.txt acorss the python packages and such

VERSION=$(cat ../version.txt)
TIMESTAMP=$(date -Iseconds)
if [[ $# -gt 0 && $1 = "preconfigure" ]]; then
    VERSION_STR="__version__ = \"$VERSION\"\n__timestamp__ = \"$TIMESTAMP\""
else
    VERSION_STR="__version__ = \"$VERSION\""
fi

echo -e $VERSION_STR > ../src/CubeServer-app/cubeserver_app/_version.py
echo -e $VERSION_STR > ../src/CubeServer-api/cubeserver_api/_version.py
echo -e $VERSION_STR > ../src/CubeServer-common/cubeserver_common/_version.py
echo -e $VERSION_STR > ../src/CubeServer-beaconserver/cubeserver_beaconserver/_version.py
