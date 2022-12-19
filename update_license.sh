#!/usr/bin/env bash
# Updates the license across Python packages and such

LICENSE=$(cat LICENSE)
LICENSE_STR="__license__ = \"\"\"\n$LICENSE\n\"\"\""

echo -e "\"\"\"\n" > ./src/CubeServer-common/cubeserver_common/_license.py
cat LICENSE >> ./src/CubeServer-common/cubeserver_common/_license.py
echo -e "\n\"\"\"" >> ./src/CubeServer-common/cubeserver_common/_license.py

cp ./src/CubeServer-common/cubeserver_common/_license.py ./src/CubeServer-api/cubeserver_api/_license.py
cp ./src/CubeServer-common/cubeserver_common/_license.py ./src/CubeServer-app/cubeserver_app/_license.py
