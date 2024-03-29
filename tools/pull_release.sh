#!/usr/bin/env bash
# Pulls and updates to a given release version

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source inc/colors.sh

if [ -z $1 ]; then
    echo -e "${RED}Please provide a release version tag as a parameter.${RESTORE}"
    exit 1
fi

if [ -n "$SSH_CLIENT" ] || [ -n "$SSH_TTY" ]; then
        echo -e "${RED}This may be in an SSH session directly."
        echo -e "Such behavior could be dangerous, as the build could terminate prematurely-"
        echo -e "Consider running this in a screen session:"
        echo -e "${CYAN}screen -L bash ./toole/pull_release.sh${RESTORE}"
fi

PREV_VER=$(cat ../version.txt)

function abort {
    git stash pop  # Prevent stashed changes from being lost in a failed update
    echo -e "${CYAN}Aborted.${RESTORE}"
    exit 1
}

function update_release {
    echo -e "${PURPLE}Updating to release ${1}...${RESTORE}\n"

    echo -e "${BLUE}  Syncing new changes... ${RED}"
    cd ..
    echo -e "    Clearing stash... "
    git stash clear
    echo -e "    Stashing changes... "
    git stash
    echo -e "    Pulling release... "
    git pull origin $1 --ff-only || abort

    echo -e "${BLUE}  Checkout Release... ${RED}"
    git config advice.detachedHead false
    git checkout "$1"

    echo -e "    Popping stashed changes... "
    git stash pop

    echo -e "${BLUE}  Configuring... ${RESTORE}"
    ./configure

    # No longer do we build locally when we can pull.
    #echo -e "${BLUE}  Building... ${RESTORE}"
    #docker compose build --parallel || abort
    #echo -e "${GREEN}  Done Building! ${RESTORE}"

    echo -e "${BLUE}  Pulling... ${RESTORE}"
    docker compose pull

    echo -e "${BLUE}  Recreating images... ${RESTORE}"
    docker compose up --force-recreate -d

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
