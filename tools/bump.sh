#!/usr/bin/env bash
# Bumps the version to the semver specified in the first argument.

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cd "$parent_path"
source inc/colors.sh

RELEASE=$1

# Exit if no version specified
if [ -z "$RELEASE" ]
then
    echo -e "${RED}  No version specified. Exiting.${RESTORE}"
    exit 1
fi

# Exit if version does not match semver
if [[ ! $RELEASE =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]
then
    echo -e "${RED}  Version does not match semver. Exiting.${RESTORE}"
    exit 1
fi

echo -e "${PURPLE}Bumping version to ${RELEASE}...${RESTORE}\n"

echo -e "${BLUE}  Getting latest develop code... ${RESTORE}"
git checkout develop
git pull
echo -e "${BLUE}  Creating release branch... ${RESTORE}"
git branch release-${RELEASE}
git checkout release-${RELEASE}
git merge develop

echo -e "${BLUE}  Updating version in release branch... ${RESTORE}"
echo ${RELEASE} > version.txt
./clean
git commit -am "bumped version"

echo -e "${BLUE}  Publishing release branch... ${RESTORE}"
git push -u origin release-${RELEASE}

echo -e "${BLUE}  Merging release branch into develop and adding -dev suffix... ${RESTORE}"
git checkout develop
git pull
git merge release-${RELEASE}

NEW_VERSION=$(echo $RELEASE | awk -F. '{$3++; print}' OFS=.)
echo ${RELEASE}-dev > version.txt
./clean
git commit -am "Started new development version ${NEW_VERSION}"

git push


echo -e "\n${LGREEN}Finished bumping version.${RESTORE}"
echo
echo -e "${CYAN}Next steps:${RESTORE}"
echo -e "${CYAN}    PR a merge from release-${RELEASE} to main"
echo -e "    then create a tag v${RELEASE} and publish a version with it ${RESTORE}"

