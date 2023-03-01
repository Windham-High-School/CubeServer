#!/usr/bin/env bash
# Copies a Docker volume $1 to $2
function vol_cp {
    echo -e "    Creating backup volume${RED}"
    docker volume create --name $2
    echo -e "${RESTORE}    Copying data to backup volume${RED}"
    docker run --rm \
               -i \
               -t \
               -v $1:/from \
               -v $2:/to \
               alpine ash -c "cd /from ; cp -av . /to"
    echo -e "${RESTORE}"
}
