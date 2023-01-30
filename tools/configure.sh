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

echo -e "\n${LGREEN}Finished Configuring.${RESTORE}"
echo -e "\nReady to run ${CYAN}docker compose build${RESTORE}\n"
