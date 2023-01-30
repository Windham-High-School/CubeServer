#!/usr/bin/env bash
# Tidys the repo. Good to run before commits

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source inc/colors.sh

echo -e "${PURPLE}Cleaning repo...${RESTORE}\n"


echo -e "${BLUE}  Cleaning Sphinx docs... ${RESTORE}"
cd ../docs
echo -e "    Running \"make clean\""
make clean 2>/dev/null 1>/dev/null


echo -e "${BLUE}  Cleaning installed config.py... ${RESTORE}"
cd "$parent_path"
rm ../src/CubeServer-common/cubeserver_common/config.py 2>/dev/null && echo "    Done." || echo "    [nonexistent]"

echo -e "${BLUE}  Updating constants... ${RESTORE}"

echo -e "    Updating license strings"
source inc/update_license.sh
echo -e "    Updating version strings"
source inc/update_version.sh

echo -e "\n${LGREEN}Finished cleaning.${RESTORE}"
