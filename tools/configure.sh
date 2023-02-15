#!/usr/bin/env bash
# Copies/installs config before build

# TODO: Check for docker-compose and install if needed

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source inc/colors.sh

./clean.sh

echo -e "\n\n${PURPLE}Configuring...${RESTORE}\n"

echo -e "${BLUE}  Checking config.py... ${RED}"
python3 ../config.py || { echo -e "${LRED}Invalid config.py; please fix.${RESTORE}" && exit 1; }

echo -e "${BLUE}  Installing config.py... ${RESTORE}"
cp ../config.py ../src/CubeServer-common/cubeserver_common/

echo -e "${BLUE}  Generating .env docker-compose config... ${RED}"
VERSION_STR=$(cat ../version.txt)
echo -e "# !! DO NOT EDIT THIS AUTOGENERATED FILE !!\n#EDIT config.env INSTEAD!\n\n"  > ../.env
grep -o '^[^#]*' ../config.env >> ../.env
echo -e "\n# Automatically copied version tag (from version.txt- copied by configure):" >> ../.env
echo -e "VERSION_TAG=\"${VERSION_STR}\"\n"          >> ../.env

echo -e "\n${LGREEN}Finished Configuring.${RESTORE}"
echo -e "\nReady to run ${CYAN}docker compose build${RESTORE} or ${CYAN}docker compose pull${RESTORE}\n"
