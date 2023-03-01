#!/usr/bin/env bash
# Updates the license across Python packages and such

echo -e "__license__ = \"\"\"\n" > ../src/CubeServer-common/cubeserver_common/_license.py
cat ../LICENSE >> ../src/CubeServer-common/cubeserver_common/_license.py
echo -e "\n\"\"\"\n" >> ../src/CubeServer-common/cubeserver_common/_license.py

cp ../src/CubeServer-common/cubeserver_common/_license.py ../src/CubeServer-api/cubeserver_api/_license.py
cp ../src/CubeServer-common/cubeserver_common/_license.py ../src/CubeServer-app/cubeserver_app/_license.py
cp ../src/CubeServer-common/cubeserver_common/_license.py ../src/CubeServer-beaconserver/cubeserver_beaconserver/_license.py
