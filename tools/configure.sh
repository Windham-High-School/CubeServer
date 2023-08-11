#!/usr/bin/env bash
# Copies/installs config before build

# TODO: Check for docker-compose and install if needed

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source inc/colors.sh
source inc/getarch.sh

echo -e "${RED}THIS SCRIPT IS OBSOLETE AND KEPT ONLY FOR DEVELOPMENT PURPOSES.${RESTORE}"
echo -e "${RED}It will be deleted shortly.${RESTORE}"
exit 1

./clean.sh preconfigure

echo -e "\n\n${PURPLE}Configuring...${RESTORE}\n"

echo -e "${BLUE}  Checking config.py... ${RED}"
python3 ../config.py || { echo -e "${LRED}Invalid config.py; please fix.${RESTORE}" && exit 1; }

echo -e "${BLUE}  Installing config.py... ${RESTORE}"
cp ../config.py ../src/CubeServer-common/cubeserver_common/
echo -e "${BLUE}  Appending AUTHORS.yaml... ${RESTORE}"
echo -e " = \"\"\"" >> ../src/CubeServer-common/cubeserver_common/config.py
grep -o '^[^#]*' ../AUTHORS.yaml >> ../src/CubeServer-common/cubeserver_common/config.py
echo -e "\"\"\"" >> ../src/CubeServer-common/cubeserver_common/config.py

echo -e "${BLUE}  Generating .env docker-compose config... ${RED}"

# Architecture-specific; see [issue #60](https://github.com/Windham-High-School/CubeServer/issues/60)
CPUARCH=$(getarch)
echo -e "    CPU Architecture: $CPUARCH"
case $CPUARCH in  # If necessary, use unofficial mongo for arm64v8
    x86_64 | arm64v8.2)
        MONGO_CONTAINER_STR="mongo"
        ;;
    arm64v8)
        MONGO_CONTAINER_STR="arm64v8/mongo"
        ;;
    *)
        echo "    Incompatible CPU Architecture!"
        exit 1
        ;;
esac

VERSION_STR=$(cat ../version.txt)
LOGLEVEL_STR=$(python3 -c "import sys;sys.path.append('..');from config import LOGGING_LEVEL;print({10:'debug',20:'info',30:'warning',40:'error',50:'critical'}[LOGGING_LEVEL])")
echo -e "# !! DO NOT EDIT THIS AUTOGENERATED FILE !!\n# EDIT config.env INSTEAD!\n\n"  > ../.env
grep -o '^[^#]*' ../config.env                          >> ../.env
echo -e "\n# Automatically generated:"                  >> ../.env
echo -e "VERSION_TAG=\"${VERSION_STR}\"\n"              >> ../.env
echo -e "LOGLEVEL=\"${LOGLEVEL_STR}\"\n"                >> ../.env
echo -e "MONGO_CONTAINER=\"${MONGO_CONTAINER_STR}\"\n"  >> ../.env
echo -e "\n${LGREEN}Finished Configuring.${RESTORE}"
echo -e "\nReady to run ${CYAN}docker compose build${RESTORE} or ${CYAN}docker compose pull${RESTORE}\n"

exit 0
