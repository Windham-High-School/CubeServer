#!/usr/bin/env bash
# Creates a backup of the docker volumes

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source inc/colors.sh
source inc/vol_cp.sh

if [ -z $1 ]; then
    bak_id=$(date "+%F_%H-%M-%S")
else
    bak_id=$1
fi

echo -e "${PURPLE}Creating volume backups...${RESTORE}\n"

echo -e "${BLUE}  MongoDB Database ${RESTORE}"
vol_cp "cubeserver_mongodb-data" "cubeserver_mongodb-data-${bak_id}"

echo -e "${BLUE}  API SSL Cert ${RESTORE}"
vol_cp "cubeserver_api-ssl-cert" "cubeserver_api-ssl-cert-${bak_id}"

echo -e "${BLUE}  Flask Secret ${RESTORE}"
vol_cp "cubeserver_flask-secret" "cubeserver_flask-secret-${bak_id}"

echo -e "\n${GREEN}Finished making backups.${RESTORE}"
