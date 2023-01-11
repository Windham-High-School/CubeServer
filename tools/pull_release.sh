#!/usr/bin/env bash
# Pulls and updates to a given release version

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source inc/colors.sh

if [ -z $1 ]; then
    echo -e "${RED}Please provide a release version tag as a parameter.${RESTORE}"
    exit 1
fi

PREV_VER=$(cat ../version.txt)

function abort {
    echo -e "${CYAN}Aborted.${RESTORE}"
    exit 1
}

function update_release {
    echo -e "${PURPLE}Updating to release ${1}...${RESTORE}\n"

    echo -e "${BLUE}  Syncing new changes... ${RED}"
    cd ..
    git pull --ff-only || abort

    echo -e "${BLUE}  Checkout Release... ${RED}"
    git config advice.detachedHead false
    git checkout "$1"

    echo -e "${BLUE}  Building... ${RESTORE}"
    docker compose build --parallel || abort
    echo -e "${GREEN}  Done Building! ${RESTORE}"

    echo -e "${BLUE}  Restarting server instances... ${RESTORE}"
    docker compose restart

    echo -e "\n${LGREEN}Finished update.${RESTORE}"
    exit
}


echo -e "${LCYAN}Are you SURE you want to update from ${PREV_VER} to ${1}?${RESTORE}"
if [ $1 = "main" ]; then
    echo -e "${LRED}It is a major risk to update to the main branch.${RESTORE}"
    echo -e "(try to pick a specific release tag instead unless this is a dev environment)\n"
fi

echo -e "This will ${RED}erase${RESTORE} any configuration changes you have made and provide a ${RED}clean build${RESTORE}."
echo -e "${RED}Please consider database compatibility${RESTORE}, etc. and know what you are doing.\n[Y/n]${LRED}"

read -r response
if [[ ${response,,} =~ ^(yes|y)$ ]]; then
    ./backup_volumes.sh "UPDATE_${PREV_VER}_to_${1}"
    update_release $1
fi
abort
