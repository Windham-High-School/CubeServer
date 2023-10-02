#!/usr/bin/env bash
# Prepares the repo for a commit

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source inc/colors.sh

# source configure.sh

echo -e "${PURPLE}Checking repo...${RESTORE}\n"


echo -e "${BLUE}  Checking bash script syntax... ${RESTORE}"
bash -n $(find tools -name *.sh)

# TODO: linting and pytest...

echo -e "\n${LGREEN}Finished checks.${RESTORE}"

# source clean.sh
