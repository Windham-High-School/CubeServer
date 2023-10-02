#!/usr/bin/env bash
# Cleans up after a docs build
#

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path/../"
source inc/colors.sh

cd ../docs/

echo -e "${PURPLE}Cleaning docs...${RESTORE}\n"


echo -e "${BLUE}  Cleaning _build... ${RESTORE}"
rm -rf _build/*
rm -rf _build/.doctrees/*
rm -f _build/.buildinfo

echo -e "${BLUE}  Cleaning apidocs... ${RESTORE}"
rm apidoc/*


