#!/usr/bin/env bash
# Builds Sphinx docs

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path/../../docs"
source ../tools/inc/colors.sh


echo -e "${PURPLE}Building docs...${RESTORE}\n"


echo -e "${BLUE}  Running apidoc... ${RESTORE}"
sphinx-apidoc --ext-autodoc -o apidoc /code/cubeserver_common
sphinx-apidoc --ext-autodoc -o apidoc /code/cubeserver_app
sphinx-apidoc --ext-autodoc -o apidoc /code/cubeserver_api


echo -e "${BLUE}  Building html docs... ${RESTORE}"
sphinx-build . _build/
